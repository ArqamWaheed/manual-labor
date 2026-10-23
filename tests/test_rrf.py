from manual_labor.ingest import Page
from manual_labor.store import rrf


def P(n: int) -> Page:
    return Page("a", n, f"page {n}")


def test_page_in_both_rankings_wins():
    bm25 = [P(21), P(3), P(9)]
    vec = [P(4), P(21), P(5)]
    assert rrf(bm25, vec, top=1)[0].page == 21


def test_keeps_top_n_and_dedupes():
    out = rrf([P(1), P(2)], [P(2), P(3)], top=3)
    assert [p.page for p in out][0] == 2 and len(out) == 3
