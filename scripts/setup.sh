#!/usr/bin/env bash
# One-shot local setup (no secrets). Run from the repo root.
set -euo pipefail
uv venv --python 3.11
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -e ".[all]"
[ -f .env ] || cp .env.example .env
command -v ollama >/dev/null && { ollama pull gemma4; ollama pull embeddinggemma; ollama pull qwen3.5:4b; } || echo "install Ollama: https://ollama.com"
command -v temporal >/dev/null || echo "install Temporal CLI: curl -sSf https://temporal.download/cli.sh | sh"
python -m manual_labor doctor
