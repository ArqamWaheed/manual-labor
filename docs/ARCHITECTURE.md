# Architecture

```
PHOTO OF PLATE -> Gemma 4 vision (local) -> brand, model
   -> SerpApi (direct PDF?) --no--> Stagehand on Browserbase (support portal, cached per brand)
   -> ingest: PDF pages -> EmbeddingGemma vectors
   -> Tiger Data: pages(vector + BM25)  · appliances(card jsonb)
        once per manual: Ultramarine compiles the card (codes, intervals, warranty, safety), cost logged
        every question:  hybrid search (BM25 + vector, RRF k=60) -> Qwen3.5-4B + Tinker LoRA (local Ollama)
                         -> steps + page, or "not in your manual"
   -> Temporal ApplianceCare workflows (timers from the card) -> ntfy push
   -> (stretch) Stagehand fills a service form -> Auth0 CIBA push -> Submit only if approved
```

## Trust boundary

Stays on the laptop: the plate photo, every question, every answer, the reminders.
Leaves once per manual: the model number (SerpApi, the support portal) and the manual text (Ultramarine).
Leaves on a tap: a technician request (Auth0-approved).
Tiger Data is hosted (us-east-1): page text and vectors live there; the question text is sent as a SQL parameter. Say this in the post.

## Single-SQL hybrid (alternative to the Python RRF in store.py)

```sql
WITH bm AS (SELECT id, row_number() OVER (ORDER BY body <@> %(q)s) r FROM pages
            WHERE appliance_id=%(a)s ORDER BY body <@> %(q)s LIMIT 20),
     vec AS (SELECT id, row_number() OVER (ORDER BY embedding <=> %(v)s::vector) r FROM pages
            WHERE appliance_id=%(a)s ORDER BY embedding <=> %(v)s::vector LIMIT 20)
SELECT p.id, p.page, p.body, COALESCE(1.0/(60+bm.r),0)+COALESCE(1.0/(60+vec.r),0) AS rrf
FROM pages p LEFT JOIN bm USING(id) LEFT JOIN vec USING(id)
WHERE bm.id IS NOT NULL OR vec.id IS NOT NULL ORDER BY rrf DESC LIMIT %(k)s;
```
