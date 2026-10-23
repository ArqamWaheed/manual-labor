"""Cost receipts. Every paid call appends one row; the post's numbers come from these files."""
from __future__ import annotations

import csv
import time

from manual_labor.config import RESULTS

# Ultramarine prices per token (docs.paperinstruments.com/docs/ultramarine/billing, 2026-10-23).
# Re-check with GET https://api.paperinstruments.com/v1/pricing before publishing.
UM_INPUT = 0.15e-6
UM_CACHED_INPUT = 0.03e-6
UM_OUTPUT = 0.50e-6  # includes reasoning tokens


def ultramarine_usd(prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0) -> float:
    uncached = max(prompt_tokens - cached_tokens, 0)
    return uncached * UM_INPUT + cached_tokens * UM_CACHED_INPUT + completion_tokens * UM_OUTPUT


def log_run(service: str, job: str, **fields: object) -> None:
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{service}_costs.csv"
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "job": job, **fields}
    new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)
