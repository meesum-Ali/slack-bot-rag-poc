# Slack Bot RAG PoC (Local)

Quickly spin up a Postgres 16 + pgvector stack on Apple‑silicon and play with Google Gemini free embeddings.

## Quick‑start

```bash
# 1 — clone repo & enter
cp .env.example .env          # paste your Gemini key
docker compose up -d          # spins Postgres + pgvector

# 2 — install Python deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3 — load sample data
echo -e "Slack bots are fun\nVectors rock\nBazaar builds grocery tech" > slack.txt
python main.py --ingest slack.txt

# 4 — query
python main.py --query "How do vectors work?"
```

**Expected output**

```
 1.  0.873  Vectors rock
 2.  0.844  Slack bots are fun
 3.  0.613  Bazaar builds grocery tech
```
*(Note: Exact scores may vary slightly with model changes or different datasets.)*

## Files

* `docker-compose.yml` – runs Postgres 16 + pgvector on ARM  
* `init.sql` – creates extension, table, HNSW index  
* `main.py` – embeds & queries with Gemini (`text-embedding-004`). Embeddings are configured to a dimension of 768 (using `TARGET_DIM` in `main.py` and `VECTOR(768)` in `init.sql`) to reduce footprint.
* `.env.example` – env vars to copy into `.env`  
* `requirements.txt` – minimal Python deps

## Extending this PoC

This proof-of-concept can be extended in several ways:

*   **Data Ingestion:** Modify `ingest()` in `main.py` to load data from other sources (e.g., different file formats, APIs, databases).
*   **Embedding Models:** Change `MODEL_NAME` and potentially `TARGET_DIM` in `main.py` (and `init.sql` if dimension changes) to experiment with other models.
*   **Vector Store:** Replace `psycopg2` interactions with clients for other vector databases (e.g., Pinecone, Weaviate, ChromaDB) if scaling or different features are needed.
*   **RAG Logic:** Expand `search()` and integrate with a language model for question answering based on retrieved documents.
