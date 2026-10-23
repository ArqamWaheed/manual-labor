"""Find a manual PDF for brand + model with SerpApi (free plan: 250 searches/month)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from manual_labor.config import DATA, settings
from manual_labor.net import get_json

CACHE = DATA / "serp_cache"


def search(query: str) -> list[dict]:
    """One Google search through SerpApi, cached on disk so reruns cost 0 searches."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (re.sub(r"[^a-z0-9]+", "_", query.lower())[:120] + ".json")
    if key.exists():
        return json.loads(key.read_text())
    s = settings()
    data = get_json(
        "https://serpapi.com/search.json",
        {"engine": "google", "q": query, "num": 10, "api_key": s.serpapi_key},
    )
    results = data.get("organic_results", [])
    key.write_text(json.dumps(results))
    return results


def find_manual(brand: str, model: str) -> list[dict]:
    """Return candidates ranked: direct PDFs whose URL/title contains the model number first."""
    seen, out = set(), []
    for q in (f'"{brand} {model}" manual filetype:pdf', f"{brand} {model} user manual support"):
        for r in search(q):
            link = r.get("link", "")
            if link in seen:
                continue
            seen.add(link)
            text = (link + " " + r.get("title", "")).lower()
            out.append({
                "url": link,
                "title": r.get("title"),
                "is_pdf": link.lower().endswith(".pdf"),
                "model_match": model.lower().replace(" ", "") in text.replace(" ", ""),
            })
    out.sort(key=lambda c: (not c["is_pdf"], not c["model_match"]))
    # TODO: log per-appliance hit (top-5 contains the right PDF?) to results/finder.csv for the post.
    return out


def download(url: str, dest: Path) -> Path:
    import urllib.request

    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (manual-labor)"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        dest.write_bytes(r.read())
    return dest
