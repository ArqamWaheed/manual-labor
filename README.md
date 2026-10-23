# Manual Labor

Nobody in the house reads the appliance manual, so the laptop does.

Photograph the rating plate once. Manual Labor finds the manual, stores every page for keyword + vector search, has a frontier model read it **once** to write an "appliance card" (error codes, maintenance intervals, warranty, safety lines), and from then on answers questions **locally** with a fine-tuned 4B model that cites the page, or says "that's not in your manual". Maintenance reminders run as durable workflows.

Built for the DEV [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).

> Status: scaffold. Commands exist as stubs with TODOs. See `memory.md`.

## How it works

| Step | Tech | Runs where |
|---|---|---|
| Read the rating plate | Gemma 4 (vision) via Ollama | local |
| Find the manual | SerpApi, then Stagehand on Browserbase for support portals | cloud (manual only, never your question) |
| Store pages | Tiger Data: pgvector (EmbeddingGemma) + pg_textsearch BM25, fused with RRF | Tiger free service |
| Compile the card | Ultramarine (`ultramarine-1-flash`), once per manual, cost logged | hosted, once |
| Answer | Qwen3.5-4B + LoRA trained on Tinker, merged to GGUF, served by Ollama | local |
| Remind | Temporal workflow per appliance, ntfy push | local |
| Book a technician (stretch) | Stagehand fills the form, Auth0 CIBA approval before Submit | cloud, after a tap |

## Run it

```bash
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e ".[all]"            # or just: python -m manual_labor --help (no deps needed)
cp .env.example .env                   # fill keys
python -m manual_labor doctor          # checks keys and services
python -m manual_labor db-init         # creates tables + indexes on Tiger Data
python -m manual_labor add --photo data/plates/ac.jpg
python -m manual_labor ask "what does E4 mean" --appliance <slug>
python -m manual_labor serve           # family page on http://0.0.0.0:8000
```

Local services: `ollama serve` and `temporal server start-dev --db-filename .temporal.db`.

## Evals

- `python scripts/eval_retrieval.py` — vector vs BM25 vs hybrid recall@k on `eval/questions.jsonl`
- `python scripts/eval_answers.py` — base vs LoRA vs Gemma 4 vs Ultramarine: citation, abstention, made-up answers
- `python scripts/usage_receipt.py` — Ultramarine spend from logged `usage` vs `GET /v1/usage`

Results land in `results/`. No number goes into the write-up unless it is in `results/`.

## Post-deadline commits

The submission deadline is 2026-10-26 06:59 UTC. Any commit after it is listed here:

- _none yet_

## Credits and prior work

- [Stagehand](https://github.com/browserbase/stagehand) (MIT) and [Browserbase](https://www.browserbase.com) for browser automation.
- [Tinker](https://tinker-docs.thinkingmachines.ai/) SDK and `tinker_cookbook` (training loop and the export/merge path follow their docs).
- [Temporal](https://temporal.io) Python SDK; [pg_textsearch](https://github.com/timescale/pg_textsearch) and [pgvector](https://github.com/pgvector/pgvector) on [Tiger Data](https://www.tigerdata.com).
- [Ollama](https://ollama.com), Google's Gemma 4 and EmbeddingGemma, Qwen3.5 by the Qwen team.
- [Ultramarine](https://docs.paperinstruments.com/docs/ultramarine) by Paper Instruments.
- The "agent stops at Submit and asks your phone" pattern was shown this week by Sloth Errands (DEV: anishisbusy).

## License

MIT, see `LICENSE`.
