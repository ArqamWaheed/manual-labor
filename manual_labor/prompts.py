"""Prompts and JSON schemas. Keep them short; retune for Ultramarine separately (its docs say so)."""

PLATE_PROMPT = (
    "This is a photo of an appliance rating plate or sticker. Return JSON only: "
    '{"brand": str, "model": str, "serial": str|null, "kind": "ac|washer|fridge|microwave|geyser|ups|other"}. '
    "Copy the model number exactly as printed. If unreadable, use null."
)

CARD_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["appliance", "error_codes", "maintenance", "warranty", "safety"],
    "properties": {
        "appliance": {"type": "string"},
        "error_codes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["code", "meaning", "user_fix", "call_service", "page"],
                "properties": {
                    "code": {"type": "string"},
                    "meaning": {"type": "string"},
                    "user_fix": {"type": "string"},
                    "call_service": {"type": "boolean"},
                    "page": {"type": "integer"},
                },
            },
        },
        "maintenance": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["task", "every_days", "page"],
                "properties": {
                    "task": {"type": "string"},
                    "every_days": {"type": "integer"},
                    "page": {"type": "integer"},
                },
            },
        },
        "warranty": {"type": "string"},
        "safety": {"type": "array", "items": {"type": "string"}},
    },
}

CARD_PROMPT = (
    "You are given the full text of one appliance manual, page by page, each page starting with "
    "'[page N]'. Extract only what the manual states. Every item must carry the page it came from. "
    "every_days: convert 'every 2 weeks' to 14, 'monthly' to 30, 'every 3 months' to 90. "
    "If the manual has no error-code table, return an empty list. Do not add advice the manual lacks."
)

ANSWER_SYSTEM = (
    "You answer household questions about one appliance using ONLY the manual pages given. "
    'Reply with JSON only. If the pages answer it: {"steps": [str, ...], "pages": [int, ...], '
    '"call_service": bool}. Use at most 6 short steps, in the language of the question. '
    'If the pages do not answer it: {"not_in_manual": true}. Never use outside knowledge.'
)


def render_pages(pages: list) -> str:
    return "\n\n".join(f"[page {p.page}]\n{p.body}" for p in pages)


def render_question(question: str, pages: list) -> str:
    return f"Manual pages:\n{render_pages(pages)}\n\nQuestion: {question}"
