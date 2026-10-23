"""Settings from environment (and a stdlib .env loader, so no python-dotenv dependency)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DATA = ROOT / "data"


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimal KEY=VALUE loader. Existing env vars win. Strips trailing '# comments'."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    ollama_host: str
    plate_model: str
    embed_model: str
    embed_dim: int
    answer_model: str
    tiger_url: str
    keyword_search: str
    ultramarine_key: str
    ultramarine_base_url: str
    ultramarine_model: str
    ultramarine_effort: str
    serpapi_key: str
    browserbase_key: str
    use_browserbase: bool
    stagehand_model: str
    stagehand_model_key: str
    temporal_address: str
    temporal_namespace: str
    temporal_queue: str
    ntfy_topic: str
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_user_sub: str


def settings() -> Settings:
    load_dotenv()
    return Settings(
        ollama_host=env("OLLAMA_HOST", "http://localhost:11434"),
        plate_model=env("PLATE_MODEL", "gemma4"),
        embed_model=env("EMBED_MODEL", "embeddinggemma"),
        embed_dim=int(env("EMBED_DIM", "768")),
        answer_model=env("ANSWER_MODEL", "manual-labor-4b"),
        tiger_url=env("TIGER_DATABASE_URL"),
        keyword_search=env("KEYWORD_SEARCH", "bm25"),
        ultramarine_key=env("PAPERINSTRUMENTS_API_KEY"),
        ultramarine_base_url=env("ULTRAMARINE_BASE_URL", "https://api.paperinstruments.com/v1"),
        ultramarine_model=env("ULTRAMARINE_MODEL", "ultramarine-1-flash"),
        ultramarine_effort=env("ULTRAMARINE_EFFORT", "high"),
        serpapi_key=env("SERPAPI_API_KEY"),
        browserbase_key=env("BROWSERBASE_API_KEY"),
        use_browserbase=env("USE_BROWSERBASE", "0") == "1",
        stagehand_model=env("STAGEHAND_MODEL", "groq/openai/gpt-oss-120b"),
        stagehand_model_key=env("STAGEHAND_MODEL_API_KEY"),
        temporal_address=env("TEMPORAL_ADDRESS", "localhost:7233"),
        temporal_namespace=env("TEMPORAL_NAMESPACE", "default"),
        temporal_queue=env("TEMPORAL_TASK_QUEUE", "manual-labor"),
        ntfy_topic=env("NTFY_TOPIC"),
        auth0_domain=env("AUTH0_DOMAIN"),
        auth0_client_id=env("AUTH0_CLIENT_ID"),
        auth0_client_secret=env("AUTH0_CLIENT_SECRET"),
        auth0_user_sub=env("AUTH0_USER_SUB"),
    )
