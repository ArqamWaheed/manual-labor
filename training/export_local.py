"""Tinker LoRA -> merged HF model -> GGUF -> Ollama (runs on the family laptop, no GPU).

Steps (per tinker-docs cookbook/deployment/export-hf):
  1. weights.download(tinker_path=TINKER_CHECKPOINT, output_dir="adapter")
  2. weights.build_hf_model(base_model="Qwen/Qwen3.5-4B", adapter_path="adapter", output_path="merged_model")
  3. llama.cpp:  python convert_hf_to_gguf.py merged_model --outfile models/manual-labor-4b-f16.gguf
                 llama-quantize models/manual-labor-4b-f16.gguf models/manual-labor-4b-Q4_K_M.gguf Q4_K_M
  4. ollama create manual-labor-4b -f training/Modelfile
Unverified: step 3 on a merged Qwen3.5-4B (Ollama ships qwen3.5:4b, so the architecture is supported).
Fallback: serve the checkpoint via Tinker's OpenAI-compatible endpoint and say it's hosted.
"""
from __future__ import annotations

import os


def main() -> None:
    from tinker_cookbook import weights

    ckpt = os.environ["TINKER_CHECKPOINT"]
    adapter = weights.download(tinker_path=ckpt, output_dir="adapter")
    weights.build_hf_model(base_model=os.environ.get("TINKER_BASE_MODEL", "Qwen/Qwen3.5-4B"),
                           adapter_path=adapter, output_path="merged_model")
    print("merged_model/ written. Next: llama.cpp convert + quantize, then `ollama create` (see docstring).")


if __name__ == "__main__":
    main()
