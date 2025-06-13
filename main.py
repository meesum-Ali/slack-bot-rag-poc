#!/usr/bin/env python3
"""
Minimal local RAG demo:
1. Ingest an array of texts (embeds + stores)
2. Run a similarity search

Run:  python main.py --ingest  slack.txt
      python main.py --query   "How do vectors work?"
"""

import os, sys, argparse, time
from typing import List
from dotenv import load_dotenv
import psycopg2, numpy as np
from psycopg2.extras import execute_values
from google import genai
from google.genai.types import EmbedContentConfig
from tqdm import tqdm

# --------------------------------------------------------------------- config
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    sys.exit("❌  GEMINI_API_KEY missing (see .env.example)")

DB_DSN = {
    "dbname": os.getenv("PGDATABASE", "vectordb"),
    "user": os.getenv("PGUSER", "demo"),
    "password": os.getenv("PGPASSWORD", "demo_pass"),
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
}

MODEL_NAME = "gemini-embedding-exp-03-07"           # free tier
TARGET_DIM = 768                                    # reduce footprint (opt.)
BATCH = 200                                         # max per free-tier call

# ------------------------------------------------------------------- helpers
genai.configure(api_key=GEMINI_KEY)

def embed_batch(texts: List[str]) -> List[List[float]]:
    cfg = EmbedContentConfig(
        output_dimensionality=TARGET_DIM,
        task_type="SEMANTIC_SIMILARITY"
    )
    resp = genai.Client().models.embed_content(
        model=MODEL_NAME,
        contents=texts,
        config=cfg
    )
    return resp.embeddings

def embed_all(texts: List[str]) -> List[List[float]]:
    out = []
    for i in tqdm(range(0, len(texts), BATCH), desc="Embedding"):
        out.extend(embed_batch(texts[i:i + BATCH]))
        time.sleep(0.2)  # stay within free-tier RPS
    return out

def ingest(path: str):
    with open(path, "r") as f:
        docs = [l.strip() for l in f if l.strip()]

    vecs = embed_all(docs)

    with psycopg2.connect(**DB_DSN) as conn, conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO docs (text, embedding) VALUES %s",
            list(zip(docs, vecs))
        )
        conn.commit()
    print(f"✅  Inserted {len(docs)} rows")

def search(query: str, k: int = 5):
    qvec = embed_batch([query])[0]
    with psycopg2.connect(**DB_DSN) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT text,
                   1 - (embedding <=> %s::vector) AS score
            FROM   docs
            ORDER  BY embedding <=> %s::vector
            LIMIT  %s
            """,
            (qvec, qvec, k),
        )
        rows = cur.fetchall()
    for rank, (txt, score) in enumerate(rows, 1):
        print(f"{rank:>2}.  {score:.3f}  {txt}")

# --------------------------------------------------------------------  CLI
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", help="Path to newline-separated texts to load")
    ap.add_argument("--query",  help="Run a similarity search")
    args = ap.parse_args()

    if args.ingest:
        ingest(args.ingest)
    elif args.query:
        search(args.query)
    else:
        ap.print_help()
