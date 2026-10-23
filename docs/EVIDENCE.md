# Evidence checklist (no artifact, no category)

| Category | Artifact | Path | Done |
|---|---|---|---|
| Ultramarine | per-call cost log; GET /v1/usage before/after screenshot; one card JSON | results/ultramarine_costs.csv, results/ultramarine_receipt.json, docs/images/ | [ ] |
| Tinker | eval table base vs LoRA vs Gemma 4 vs Ultramarine; Tinker billing total; checkpoint path; `ollama show manual-labor-4b` | results/answers_eval.json, results/train_log.json | [ ] |
| Tiger Data | vector vs BM25 vs hybrid recall@5 (code/plain split); `\d+ pages` showing hnsw + bm25 | results/retrieval_eval.json | [ ] |
| Browserbase | session list (count, minutes); replay screenshot; run 1 vs cached run 2 | results/browser_costs.csv, docs/images/ | [ ] |
| SerpApi | per-appliance top-5 hit; searches used | results/finder.csv | [ ] |
| Temporal | UI screenshot; kill drill; time-skip output | results/temporal_timeskip.txt, docs/images/ | [ ] |
| Entire | >= 3 session/checkpoint links; one search that explained a decision | post | [ ] |
| Auth0 (stretch) | Guardian push screenshot with binding message; approved + denied logs | docs/images/, results/ | [ ] |
| Gemma | plate photo -> JSON example; EmbeddingGemma in store; Gemma 4 eval row | docs/images/, results/answers_eval.json | [ ] |
