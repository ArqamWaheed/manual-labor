"""Tiger Data store: schema, upserts, and the three search modes the eval compares."""
from __future__ import annotations

from importlib import resources

from manual_labor.config import settings
from manual_labor.ingest import Page

RRF_K = 60  # standard reciprocal-rank-fusion constant; keep fixed before running evals


def connect():
    import psycopg

    return psycopg.connect(settings().tiger_url, autocommit=True)


def init_db() -> dict:
    status = {}
    with connect() as c:
        c.execute(resources.files("manual_labor").joinpath("sql/schema.sql").read_text())
        status["schema"] = "ok"
        try:
            c.execute(resources.files("manual_labor").joinpath("sql/bm25.sql").read_text())
            status["bm25"] = "ok"
        except Exception as e:  # pg_textsearch missing on this service
            status["bm25"] = f"unavailable ({e.__class__.__name__}); use KEYWORD_SEARCH=tsvector"
    return status


def upsert_appliance(aid: str, brand: str, model: str, **cols) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO appliances (id, brand, model, kind, manual_url, source) VALUES (%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (id) DO UPDATE SET manual_url=EXCLUDED.manual_url, source=EXCLUDED.source",
            (aid, brand, model, cols.get("kind"), cols.get("manual_url"), cols.get("source")),
        )


def upsert_pages(pages: list[Page], vectors: list[list[float]]) -> None:
    with connect() as c, c.cursor() as cur:
        cur.executemany(
            "INSERT INTO pages (appliance_id, page, body, embedding) VALUES (%s,%s,%s,%s::vector) "
            "ON CONFLICT (appliance_id, page) DO UPDATE SET body=EXCLUDED.body, embedding=EXCLUDED.embedding",
            [(p.appliance_id, p.page, p.body, str(v)) for p, v in zip(pages, vectors)],
        )


def save_card(aid: str, card: dict) -> None:
    import json

    with connect() as c:
        c.execute("UPDATE appliances SET card=%s::jsonb WHERE id=%s", (json.dumps(card), aid))


def _rows(sql: str, params: dict) -> list[Page]:
    with connect() as c:
        return [Page(a, pg, body, id=i) for i, a, pg, body in c.execute(sql, params).fetchall()]


def search_vector(aid: str, qvec: list[float], k: int = 20) -> list[Page]:
    return _rows(
        "SELECT id, appliance_id, page, body FROM pages WHERE appliance_id=%(a)s "
        "ORDER BY embedding <=> %(v)s::vector LIMIT %(k)s",
        {"a": aid, "v": str(qvec), "k": k},
    )


def search_keyword(aid: str, q: str, k: int = 20) -> list[Page]:
    if settings().keyword_search == "bm25":
        # pg_textsearch: <@> returns a negative BM25 score, lower = better.
        sql = ("SELECT id, appliance_id, page, body FROM pages WHERE appliance_id=%(a)s "
               "ORDER BY body <@> %(q)s LIMIT %(k)s")
    else:
        sql = ("SELECT id, appliance_id, page, body FROM pages WHERE appliance_id=%(a)s "
               "AND tsv @@ websearch_to_tsquery('english', %(q)s) "
               "ORDER BY ts_rank_cd(tsv, websearch_to_tsquery('english', %(q)s)) DESC LIMIT %(k)s")
    return _rows(sql, {"a": aid, "q": q, "k": k})


def rrf(*rankings: list[Page], k: int = RRF_K, top: int = 4) -> list[Page]:
    """Reciprocal rank fusion over page lists (pure function; tested in tests/test_rrf.py)."""
    score: dict[tuple[str, int], float] = {}
    keep: dict[tuple[str, int], Page] = {}
    for ranking in rankings:
        for rank, p in enumerate(ranking, start=1):
            key = (p.appliance_id, p.page)
            score[key] = score.get(key, 0.0) + 1.0 / (k + rank)
            keep.setdefault(key, p)
    return [keep[key] for key in sorted(score, key=score.get, reverse=True)[:top]]


def search_hybrid(aid: str, q: str, top: int = 4) -> list[Page]:
    from manual_labor.ingest import embed

    qvec = embed([q])[0]
    # Fused in Python for clarity; the single-SQL version is in docs/ARCHITECTURE.md.
    return rrf(search_keyword(aid, q), search_vector(aid, qvec), top=top)
