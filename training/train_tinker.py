"""LoRA SFT on Tinker (API per tinker-docs.thinkingmachines.ai/tinker/sdk-cheatsheet).

Run (Python 3.11+, `uv pip install tinker tinker-cookbook`, TINKER_API_KEY set):
    python training/train_tinker.py --data data/train.jsonl --epochs 3
Prints the tinker:// sampler path; put it in .env as TINKER_CHECKPOINT.
"""
from __future__ import annotations

import argparse
import json
import os
import random


def to_datum(tok, prompt_text: str, completion_text: str):
    from tinker import types

    p = tok.encode(prompt_text)
    c = tok.encode(completion_text) + [tok.eos_token_id]
    full = p + c
    return types.Datum(
        model_input=types.ModelInput.from_ints(tokens=full[:-1]),
        loss_fn_inputs=dict(weights=[0.0] * (len(p) - 1) + [1.0] * len(c), target_tokens=full[1:]),
    )


def main() -> None:
    import tinker
    from tinker import types

    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/train.jsonl")
    ap.add_argument("--base", default=os.environ.get("TINKER_BASE_MODEL", "Qwen/Qwen3.5-4B"))
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-4)
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(a.data)]
    tc = tinker.ServiceClient().create_lora_training_client(base_model=a.base, rank=a.rank)
    tok = tc.get_tokenizer()
    # TODO: render prompts with the model's chat template (thinking OFF), identically to serving.
    #       tinker_cookbook.renderers has the right renderer; Ollama's Modelfile TEMPLATE must match it.
    step = 0
    for epoch in range(a.epochs):
        random.Random(epoch).shuffle(rows)
        for i in range(0, len(rows), a.batch):
            data = [to_datum(tok, r["prompt"], r["completion"]) for r in rows[i : i + a.batch]]
            fb = tc.forward_backward(data, "cross_entropy")
            tc.optim_step(types.AdamParams(learning_rate=a.lr)).result()
            fb.result()
            step += 1
        print(f"epoch {epoch + 1} done, {step} steps")
    # TODO: hold out 5% as dev, log dev loss per epoch to results/train_log.json
    sc = tc.save_weights_and_get_sampling_client(name="manual-labor-final")
    print("saved:", sc)  # TODO: print the tinker:// sampler path explicitly for TINKER_CHECKPOINT


if __name__ == "__main__":
    main()
