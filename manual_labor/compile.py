"""Ultramarine reads a whole manual once and writes the appliance card. Every call's cost is logged."""
from __future__ import annotations

import json

from manual_labor.config import settings
from manual_labor.costs import log_run, ultramarine_usd
from manual_labor.prompts import CARD_PROMPT, CARD_SCHEMA, render_pages


def client():
    from openai import OpenAI

    s = settings()
    return OpenAI(base_url=s.ultramarine_base_url, api_key=s.ultramarine_key)


def compile_card(aid: str, pages: list) -> dict:
    s = settings()
    text = render_pages(pages)
    # TODO: if the context window is smaller than the manual (unverified), split into <=40k-token parts
    #       and merge cards; record that in the post.
    r = client().chat.completions.create(
        model=s.ultramarine_model,
        reasoning_effort=s.ultramarine_effort,  # mandatory on Ultramarine: low | high | max
        max_completion_tokens=8192,              # always bound output; omission reserves 65,536 tokens
        messages=[{"role": "system", "content": CARD_PROMPT}, {"role": "user", "content": text}],
        response_format={"type": "json_schema", "json_schema": {"name": "card", "schema": CARD_SCHEMA}},
    )
    u = r.usage
    details = getattr(u, "completion_tokens_details", None)
    reasoning = getattr(details, "reasoning_tokens", 0) if details else 0
    log_run(
        "ultramarine", f"card:{aid}",
        prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens,
        reasoning_tokens=reasoning, usd=round(ultramarine_usd(u.prompt_tokens, u.completion_tokens), 6),
    )
    return json.loads(r.choices[0].message.content)


def usage_now() -> dict:
    """GET /v1/usage (current UTC month) for the receipt screenshot; balances are in nanodollars."""
    import urllib.request

    s = settings()
    req = urllib.request.Request(f"{s.ultramarine_base_url}/usage",
                                 headers={"Authorization": f"Bearer {s.ultramarine_key}"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        return json.loads(r.read())
