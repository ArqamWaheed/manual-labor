"""Vector vs BM25 vs hybrid recall@k on eval/questions.jsonl -> results/retrieval_eval.json.

Question rows: {"id", "appliance_id", "q", "gold_pages": [int], "type": "code|plain", "answerable": bool}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main(path: str = "eval/questions.jsonl", k: int = 5) -> None:
    from manual_labor import store
    from manual_labor.ingest import embed

    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows = [r for r in rows if r.get("answerable") and r.get("gold_pages")]
    modes = {"vector": [], "bm25": [], "hybrid": []}
    for r in rows:
        qv = embed([r["q"]])[0]
        got = {
            "vector": store.search_vector(r["appliance_id"], qv, k),
            "bm25": store.search_keyword(r["appliance_id"], r["q"], k),
        }
        got["hybrid"] = store.rrf(got["bm25"], got["vector"], top=k)
        for m, pages in got.items():
            ranks = [i for i, p in enumerate(pages, 1) if p.page in r["gold_pages"]]
            modes[m].append({"id": r["id"], "type": r.get("type"), "hit": bool(ranks), "rank": ranks[0] if ranks else None})
    out = {}
    for m, hits in modes.items():
        for t in ("all", "code", "plain"):
            h = [x for x in hits if t == "all" or x["type"] == t]
            if h:
                out[f"{m}.{t}.recall@{k}"] = f"{sum(x['hit'] for x in h)}/{len(h)}"
                out[f"{m}.{t}.mrr"] = round(sum(1 / x["rank"] for x in h if x["rank"]) / len(h), 3)
    Path("results").mkdir(exist_ok=True)
    Path("results/retrieval_eval.json").write_text(json.dumps({"summary": out, "rows": modes}, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:])
