"""Answer eval: base vs LoRA vs Gemma 4 vs Ultramarine on held-out questions -> results/answers_eval.json.

Same contexts for every model (top-4 hybrid pages), temperature 0.
Metrics: cite_ok (answerable, cited a gold page), abstain_ok (unanswerable, said not-in-manual),
made_up (unanswerable, answered anyway), false_abstain (answerable, refused), latency p50.
--blind writes answers with model names hidden to results/blind_grading.csv for hand grading of steps.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MODELS = {
    # name: (model id, base_url or None for local Ollama, api key env)
    "qwen3.5-4b-base": ("qwen3.5:4b", None, None),
    "gemma4-local": ("gemma4", None, None),
    "lora-local": ("manual-labor-4b", None, None),
    "ultramarine": ("ultramarine-1-flash", "https://api.paperinstruments.com/v1", "PAPERINSTRUMENTS_API_KEY"),
}


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def main() -> None:
    import os

    from manual_labor import store
    from manual_labor.answer import answer

    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="eval/questions.jsonl")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--blind", action="store_true")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.questions) if l.strip()]
    ctx = {r["id"]: store.search_hybrid(r["appliance_id"], r["q"]) for r in rows}
    # TODO: Ultramarine requires reasoning_effort; pass it via answer() when base_url is Ultramarine,
    #       and log its cost with costs.log_run so the "$ / 1k questions" column is real.
    report = {}
    for name in a.models.split(","):
        mid, base, keyenv = MODELS[name]
        res = []
        for r in rows:
            ans = answer(r["q"], ctx[r["id"]], model=mid, base_url=base,
                         api_key=os.environ.get(keyenv, "ollama") if keyenv else "ollama")
            res.append({"id": r["id"], "answerable": r["answerable"], "gold": r.get("gold_pages", []), **ans.__dict__})
        ans_ = [x for x in res if x["answerable"]]
        una = [x for x in res if not x["answerable"]]
        k_cite = sum(1 for x in ans_ if not x["not_in_manual"] and set(x["pages"]) & set(x["gold"]))
        k_abst = sum(1 for x in una if x["not_in_manual"])
        report[name] = {
            "cite_ok": f"{k_cite}/{len(ans_)}", "cite_ci": wilson(k_cite, len(ans_)),
            "abstain_ok": f"{k_abst}/{len(una)}", "abstain_ci": wilson(k_abst, len(una)),
            "made_up": f"{len(una) - k_abst}/{len(una)}",
            "false_abstain": f"{sum(1 for x in ans_ if x['not_in_manual'])}/{len(ans_)}",
            "p50_latency_s": round(statistics.median(x["latency_s"] for x in res), 2) if res else None,
            "rows": res,
        }
        print(name, {k: v for k, v in report[name].items() if k != "rows"})
    Path("results").mkdir(exist_ok=True)
    Path("results/answers_eval.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    # TODO --blind: shuffle (question, steps) pairs across models into results/blind_grading.csv


if __name__ == "__main__":
    main()
