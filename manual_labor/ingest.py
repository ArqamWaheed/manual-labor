"""PDF -> page text -> embeddings (EmbeddingGemma on Ollama) -> Tiger Data."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from manual_labor.config import settings
from manual_labor.net import post_json


@dataclass
class Page:
    appliance_id: str
    page: int
    body: str
    id: int | None = None


def pdf_pages(pdf: Path, appliance_id: str) -> list[Page]:
    import fitz  # pymupdf

    pages = []
    with fitz.open(pdf) as doc:
        for i, p in enumerate(doc, start=1):
            text = p.get_text("text").strip()
            if text:
                pages.append(Page(appliance_id, i, text))
    # TODO: scanned manuals have no text layer -> OCR page images with the plate model (Gemma 4 vision).
    # TODO: split very long pages into ~1,500-char chunks but keep the page number on every chunk.
    return pages


def embed(texts: list[str]) -> list[list[float]]:
    s = settings()
    # Ollama /api/embed accepts a list input and returns {"embeddings": [[...], ...]}.
    r = post_json(f"{s.ollama_host}/api/embed", {"model": s.embed_model, "input": texts})
    return r["embeddings"]


def ingest_pdf(pdf: Path, appliance_id: str, batch: int = 16) -> int:
    from manual_labor import store

    pages = pdf_pages(pdf, appliance_id)
    for i in range(0, len(pages), batch):
        chunk = pages[i : i + batch]
        vectors = embed([p.body for p in chunk])
        store.upsert_pages(chunk, vectors)
    return len(pages)
