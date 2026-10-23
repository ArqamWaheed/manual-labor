"""Ultramarine receipt: sum of logged per-call costs vs GET /v1/usage. Screenshot both for the post."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> None:
    from manual_labor.compile import usage_now

    path = Path("results/ultramarine_costs.csv")
    rows = list(csv.DictReader(path.open())) if path.exists() else []
    logged = sum(float(r["usd"]) for r in rows)
    print(f"logged calls: {len(rows)}  logged usd: {logged:.4f}")
    u = usage_now()
    print(json.dumps(u, indent=2))
    # Balances are nanodollars: 1 USD = 1,000,000,000.
    Path("results/ultramarine_receipt.json").write_text(json.dumps({"logged_usd": logged, "calls": len(rows), "usage": u}, indent=2))


if __name__ == "__main__":
    main()
