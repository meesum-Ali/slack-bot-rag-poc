-- enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- docs table for RAG chunks
CREATE TABLE IF NOT EXISTS docs (
  id         SERIAL PRIMARY KEY,
  text       TEXT,
  embedding  VECTOR(3072)          -- Gemini default dimensionality
);

-- high-recall HNSW index
CREATE INDEX IF NOT EXISTS docs_embedding_hnsw
ON docs
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
