-- Manual Labor schema for a Tiger Data free service.
-- G1 gate: both extensions must create. If pg_textsearch fails, set KEYWORD_SEARCH=tsvector.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS appliances (
  id          text PRIMARY KEY,            -- slug: brand-model
  brand       text NOT NULL,
  model       text NOT NULL,
  kind        text,
  manual_url  text,
  source      text,                        -- serpapi | browserbase | upload | photos
  card        jsonb,                       -- Ultramarine appliance card
  created_at  timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pages (
  id            bigserial PRIMARY KEY,
  appliance_id  text NOT NULL REFERENCES appliances(id) ON DELETE CASCADE,
  page          int  NOT NULL,
  body          text NOT NULL,
  embedding     vector(768),               -- match EMBED_DIM
  tsv           tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED,
  UNIQUE (appliance_id, page)
);

CREATE INDEX IF NOT EXISTS pages_embedding_hnsw ON pages USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS pages_tsv_gin ON pages USING gin (tsv);   -- fallback keyword path
CREATE INDEX IF NOT EXISTS pages_appliance ON pages (appliance_id);
