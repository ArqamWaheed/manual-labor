"""Teacher data for the Tinker LoRA (Ultramarine writes it; code checks it).

Rows: {"prompt": <system+pages+question rendered as chat>, "completion": <target JSON>, "meta": {...}}
- Uses TRAIN manuals only (see eval/split.json). Held-out manuals never appear here.
- Contexts are the pages a real hybrid search returns, so training matches serving.
- ~30% unanswerable on purpose: a question about appliance X asked with appliance Y's pages,
  or a detail the manual lacks. Target: {"not_in_manual": true}.
Run:  python training/make_dataset.py --per-manual 60 --out data/train.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

QGEN_PROMPT = (
    "From these manual pages, write {n} questions a family member might ask, in English, Roman Urdu, "
    "or both mixed. Mix error codes, cleaning, settings and safety. For each, give the answer steps "
    "and the page numbers that support it. JSON: {\"items\": [{\"q\": str, \"steps\": [str], \"pages\": [int]}]}"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-manual", type=int, default=60)
    ap.add_argument("--unanswerable", type=float, default=0.3)
    ap.add_argument("--out", default="data/train.jsonl")
    a = ap.parse_args()
    split = json.loads(Path("eval/split.json").read_text())  # {"train": [...ids], "heldout": [...ids]}
    random.seed(7)
    # TODO 1: for each train appliance, call Ultramarine (compile.client()) with QGEN_PROMPT over its pages,
    #         reasoning_effort="high", max_completion_tokens=8192; log cost via costs.log_run.
    # TODO 2: for each item, pages = store.search_hybrid(aid, q) ; if the gold pages aren't in `pages`,
    #         either drop the row or make it an unanswerable row (the retrieval didn't find it).
    # TODO 3: unanswerables: take a question from appliance X, retrieve with appliance Y's id -> not_in_manual.
    # TODO 4: spot-check 30 random rows by hand; write the error count to results/teacher_check.json.
    # TODO 5: write rows to a.out; never include any heldout id (assert).
    raise SystemExit("make_dataset: TODOs above")


if __name__ == "__main__":
    main()
