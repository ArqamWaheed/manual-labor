"""Read a rating-plate photo with Gemma 4 (vision) on local Ollama."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from manual_labor.config import settings
from manual_labor.net import post_json
from manual_labor.prompts import PLATE_PROMPT


def read_plate(photo: Path) -> dict:
    s = settings()
    img = base64.b64encode(Path(photo).read_bytes()).decode()
    # Ollama chat API: images are base64 strings on the message; format="json" forces JSON output.
    r = post_json(
        f"{s.ollama_host}/api/chat",
        {
            "model": s.plate_model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [{"role": "user", "content": PLATE_PROMPT, "images": [img]}],
        },
    )
    out = json.loads(r["message"]["content"])
    # TODO: normalise model numbers (strip spaces, O vs 0) and keep the raw string for the post.
    return out


def slug(brand: str, model: str) -> str:
    return f"{brand}-{model}".lower().replace(" ", "").replace("/", "-")
