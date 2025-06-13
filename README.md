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

## Files

* `docker-compose.yml` – runs Postgres 16 + pgvector on ARM  
* `init.sql` – creates extension, table, HNSW index  
* `main.py` – embeds & queries with Gemini (`gemini-embedding-exp-03-07`)  
* `.env.example` – env vars to copy into `.env`  
* `requirements.txt` – minimal Python deps
