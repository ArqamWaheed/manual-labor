-- pg_textsearch BM25 (Tiger Data). Applied separately so a missing extension doesn't break schema.sql.
CREATE EXTENSION IF NOT EXISTS pg_textsearch;
CREATE INDEX IF NOT EXISTS pages_bm25 ON pages USING bm25 (body) WITH (text_config = 'english');
