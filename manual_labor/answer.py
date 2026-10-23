"""The local answerer: retrieved pages in, steps + page numbers (or an honest abstention) out."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

from manual_labor.config import settings
from manual_labor.prompts import ANSWER_SYSTEM, render_question


@dataclass
class Answer:
    steps: list[str] = field(default_factory=list)
    pages: list[int] = field(default_factory=list)
    call_service: bool = False
    not_in_manual: bool = False
    reason: str = ""
    latency_s: float = 0.0
    model: str = ""

    @classmethod
    def abstain(cls, reason: str, **kw) -> "Answer":
        return cls(not_in_manual=True, reason=reason, **kw)


def parse_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()  # Qwen thinking blocks, if any
    m = re.search(r"\{.*\}", text, flags=re.S)
    return json.loads(m.group(0)) if m else {}


def answer(question: str, pages: list, model: str | None = None, base_url: str | None = None,
           api_key: str = "ollama") -> Answer:
    """Default target is local Ollama (OpenAI-compatible). Baselines pass another model/base_url."""
    from openai import OpenAI

    s = settings()
    model = model or s.answer_model
    client = OpenAI(base_url=base_url or f"{s.ollama_host}/v1", api_key=api_key)
    t0 = time.perf_counter()
    r = client.chat.completions.create(
        model=model, temperature=0,
        messages=[{"role": "system", "content": ANSWER_SYSTEM},
                  {"role": "user", "content": render_question(question, pages)}],
    )
    dt = time.perf_counter() - t0
    try:
        out = parse_json(r.choices[0].message.content or "")
    except json.JSONDecodeError:
        return Answer.abstain("unparseable output", latency_s=dt, model=model)
    if out.get("not_in_manual"):
        return Answer.abstain("not in your manual", latency_s=dt, model=model)
    retrieved = {p.page for p in pages}
    cited = [int(x) for x in out.get("pages", []) if str(x).isdigit()]
    # The rule that matters: citing a page we didn't retrieve means the model used outside knowledge.
    if not cited or not set(cited) <= retrieved:
        return Answer.abstain("cited a page that wasn't retrieved", latency_s=dt, model=model)
    return Answer(steps=out.get("steps", [])[:6], pages=cited, call_service=bool(out.get("call_service")),
                  latency_s=dt, model=model)
