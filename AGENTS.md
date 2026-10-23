# AGENTS.md — how to work in this repo

## Loop rule
- Read `memory.md` FIRST every task. Update it LAST (summarize; don't dump; prune stale lines). Keep it short.

## Context discipline
- Edit only the files the task needs. Don't scan the whole repo; `memory.md` has the file map.
- Prefer small diffs. Keep stubs importable: `python -m manual_labor --help` must always work with no extra deps (heavy imports go inside functions).

## Design rule
- For any web UI (`manual_labor/static/`), use the `frontend-design` skill. Palette for this project: paper `#F4F1EA`, ink `#1E2A38`, accent safety-orange `#F26B1D`, rules `#9AA5B1`, IBM Plex Mono for codes.

## Commits
- After each working increment, commit with Conventional Commits: `feat|fix|docs|chore|refactor(scope): summary`. Never put secrets in messages.

## Run discipline
- Keep README run steps current. Secrets only in `.env` (git-ignored); add every new key to `.env.example` with a comment.
- Numbers: never write a result into README/docs/post unless a script in `scripts/` or `training/` produced it and saved it under `results/`.

## Honesty rules (this is a contest entry)
- Don't claim a feature works until it ran end to end. Label unfinished things "soon".
- The answerer must only use retrieved pages. Don't weaken the abstention rule to make a demo look better.
- Don't submit any real outside form without an Auth0 approval.

## Stop conditions
- Ask before large refactors, new heavy dependencies, or spending paid credits beyond the plan (Ultramarine $5 promo, Tinker credits, Browserbase 1 browser-hour).
