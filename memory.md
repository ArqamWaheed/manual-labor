# memory.md — Manual Labor brain
> Read this first every task. Update it last. Keep it terse to save tokens.

## What this is
Appliance-manual sloth: photo of rating plate -> find manual -> Tiger hybrid search -> Ultramarine compiles a card once -> local Tinker-tuned Qwen3.5-4B answers with page or "not in your manual" -> Temporal reminders -> (stretch) Auth0-approved technician request.
Entry for DEV Hacktoberfest Week 3 "Slow and Steady". Deadline 2026-10-26 06:59 UTC (Mon 11:59 PKT).

## Stack
Python 3.11 (uv). Ollama (gemma4 vision, embeddinggemma, manual-labor-4b GGUF). Tiger Data free service (pgvector + pg_textsearch). Ultramarine via OpenAI SDK. Tinker + tinker_cookbook. SerpApi. Stagehand + Browserbase. Temporal Python SDK + `temporal server start-dev`. FastAPI page. ntfy.sh. Auth0 CIBA.

## Status snapshot
- Phase: scaffold only (stubs + TODOs). No git yet.
- Last task: scaffold created from the playbook (research repo: outputs/hackathon-research/hacktoberfest-week3-2026-10/03-PLAYBOOK-manual-labor.md)
- Next: Hour 0 -> git init, Entire enable, first commit; then gates G1-G10 (`python -m manual_labor doctor`).

## Checkpoints (UTC)
CP0 Fri 22:30 gates | CP1 Sat 09:00 search+card | CP2 Sat 15:00 6 manuals, 1 via Browserbase, Tinker run 1 done | CP3 Sat 21:00 local LoRA answers + eval v1 (else drop Tinker) | CP4 Sun 09:00 Auth0 in/out | CP5 Sun 13:00 FREEZE | CP6 Sun 19:00 publish | hard latest Mon 04:59

## Key decisions (why)
- Ultramarine only compiles cards + teacher data, never answers at runtime (open AI must be the core; $0/question).
- Hybrid BM25+vector with RRF k=60: error codes are rare tokens; vectors blur them.
- Answerer cites only retrieved pages; any other cited page => abstain.
- Develop Stagehand on local Chrome; Browserbase Free = 1 browser-hour total.
- Never write a number into docs/post unless a script saved it under results/.

## Gate results (fill at CP0)
| gate | status | note |
|---|---|---|
| G1 Tiger + pg_textsearch | ? | |
| G2 Ultramarine promo | ? | |
| G3 Tinker credits | ? | |
| G4 Browserbase | ? | |
| G5 SerpApi | ? | |
| G6 Ollama models | ? | |
| G7 Temporal CLI | ? | |
| G8 Auth0 CIBA | ? | |
| G9 plates photographed | ? | |
| G10 Entire | ? | |

## Open questions / TODO
- Which manuals are train vs held-out (>=3 brands held out)
- pg_textsearch available on free service?
- Ultramarine context window (chunk <=40k tokens if unknown)

## File map (only what matters)
- `manual_labor/cli.py` — all commands (`python -m manual_labor --help`)
- `manual_labor/store.py` + `sql/schema.sql` — Tiger schema, hybrid search
- `manual_labor/compile.py` — Ultramarine card + cost log
- `manual_labor/answer.py` — local answerer + abstention rule
- `manual_labor/finder.py` / `browser.py` — SerpApi / Stagehand+Browserbase
- `manual_labor/remind.py` — Temporal ApplianceCare workflow + worker
- `manual_labor/approve.py` — Auth0 CIBA
- `training/` — dataset, Tinker SFT, export to Ollama
- `scripts/` — evals, usage receipt
- `docs/EVIDENCE.md` — per-category evidence checklist
