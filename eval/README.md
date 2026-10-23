# eval/

- `questions.jsonl` (you write it, by hand, BEFORE any model runs on it; commit it first). Format: see `questions.example.jsonl`.
  Target: >= 40 questions on held-out manuals, >= 12 unanswerable, mixed English / Roman Urdu, `type` = code|plain.
- `split.json`: which appliances are train vs held-out. Decide before `training/make_dataset.py` runs.
- `questions_fresh.jsonl`: only if prompts/data changed after looking at results. Run every model on it once.
