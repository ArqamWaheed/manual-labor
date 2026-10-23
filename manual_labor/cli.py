"""Command line. Heavy imports live inside each command so `--help` works with no dependencies."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def cmd_doctor(a: argparse.Namespace) -> int:
    from manual_labor.config import settings

    s = settings()
    checks = {
        "TIGER_DATABASE_URL": bool(s.tiger_url),
        "PAPERINSTRUMENTS_API_KEY (Ultramarine)": bool(s.ultramarine_key),
        "SERPAPI_API_KEY": bool(s.serpapi_key),
        "BROWSERBASE_API_KEY": bool(s.browserbase_key),
        "NTFY_TOPIC": bool(s.ntfy_topic),
        "AUTH0_DOMAIN (stretch)": bool(s.auth0_domain),
    }
    for k, ok in checks.items():
        print(f"[{'ok' if ok else '--'}] {k}")
    for mod in ("openai", "psycopg", "fitz", "fastapi", "stagehand", "temporalio", "tinker"):
        try:
            __import__(mod)
            print(f"[ok] import {mod}")
        except ImportError:
            print(f"[--] import {mod}")
    if a.ping == "ollama":
        from manual_labor.net import get_json
        print(json.dumps([m["name"] for m in get_json(f"{s.ollama_host}/api/tags")["models"]]))
    elif a.ping == "ultramarine":
        from manual_labor.compile import usage_now
        print(json.dumps(usage_now(), indent=2))
    elif a.ping == "serpapi":
        from manual_labor.finder import search
        print(len(search("Haier inverter AC user manual filetype:pdf")), "results")
    elif a.ping == "tiger":
        from manual_labor import store
        with store.connect() as c:
            print(c.execute("SELECT extname, extversion FROM pg_extension ORDER BY 1").fetchall())
    elif a.ping == "auth0":
        from manual_labor.approve import request_approval
        print("approved" if request_approval("Manual Labor test: approve?") else "denied/expired")
    elif a.ping == "browserbase":
        print("TODO: open+close one Browserbase session via manual_labor.browser._launch()")
    return 0


def cmd_db_init(a: argparse.Namespace) -> int:
    from manual_labor import store

    print(json.dumps(store.init_db(), indent=2))
    return 0


def cmd_add(a: argparse.Namespace) -> int:
    """Photo or brand/model -> find -> download -> ingest -> card -> reminders."""
    from manual_labor import finder, ingest, store
    from manual_labor.config import DATA
    from manual_labor.plate import read_plate, slug

    if a.photo:
        plate = read_plate(Path(a.photo))
        print("plate:", json.dumps(plate))
        brand, model = plate.get("brand"), plate.get("model")
    else:
        brand, model = a.brand, a.model
    if not (brand and model):
        print("Could not read brand/model. Pass --brand and --model.", file=sys.stderr)
        return 2
    aid = slug(brand, model)
    pdf = Path(a.pdf) if a.pdf else None
    url = None
    if pdf is None:
        cands = finder.find_manual(brand, model)
        direct = [c for c in cands if c["is_pdf"]]
        if not direct:
            print("No direct PDF. Try: python -m manual_labor fetch --support-url <url> --model", model)
            print(json.dumps(cands[:5], indent=2))
            return 3
        url = direct[0]["url"]
        pdf = finder.download(url, DATA / "manuals" / f"{aid}.pdf")
    store.upsert_appliance(aid, brand, model, manual_url=url, source="upload" if a.pdf else "serpapi")
    n = ingest.ingest_pdf(pdf, aid)
    print(f"{aid}: {n} pages stored")
    # TODO: compile card (cmd_compile) and schedule reminders (remind.schedule_card) once both are green.
    return 0


def cmd_fetch(a: argparse.Namespace) -> int:
    from manual_labor.browser import fetch_manual_links

    print(json.dumps(asyncio.run(fetch_manual_links(a.support_url, a.model)), indent=2))
    return 0


def cmd_search(a: argparse.Namespace) -> int:
    from manual_labor import store

    pages = store.search_hybrid(a.appliance, a.query, top=a.k)
    for p in pages:
        print(f"p.{p.page}: {p.body[:160].replace(chr(10), ' ')}")
    return 0


def cmd_compile(a: argparse.Namespace) -> int:
    from manual_labor import store
    from manual_labor.compile import compile_card

    with store.connect() as c:
        rows = c.execute("SELECT page, body FROM pages WHERE appliance_id=%s ORDER BY page", (a.appliance,)).fetchall()
    from manual_labor.ingest import Page
    card = compile_card(a.appliance, [Page(a.appliance, pg, b) for pg, b in rows])
    store.save_card(a.appliance, card)
    print(json.dumps(card, indent=2, ensure_ascii=False))
    return 0


def cmd_ask(a: argparse.Namespace) -> int:
    from manual_labor import store
    from manual_labor.answer import answer

    pages = store.search_hybrid(a.appliance, a.question)
    ans = answer(a.question, pages, model=a.model)
    if ans.not_in_manual:
        print(f"That isn't in your manual. ({ans.reason})")
    else:
        for i, s in enumerate(ans.steps, 1):
            print(f"{i}. {s}")
        print(f"   p. {', '.join(map(str, ans.pages))}" + ("  · call service" if ans.call_service else ""))
    print(f"[{ans.model} · {ans.latency_s:.1f}s]")
    return 0


def cmd_remind(a: argparse.Namespace) -> int:
    from manual_labor import remind, store

    if a.action == "worker":
        asyncio.run(remind.run_worker())
    else:
        with store.connect() as c:
            row = c.execute("SELECT card FROM appliances WHERE id=%s", (a.appliance,)).fetchone()
        print(asyncio.run(remind.schedule_card(a.appliance, row[0] or {})))
    return 0


def cmd_serve(a: argparse.Namespace) -> int:
    from manual_labor.config import env, load_dotenv
    from manual_labor.web import serve

    load_dotenv()
    serve(a.host or env("WEB_HOST", "0.0.0.0"), a.port or int(env("WEB_PORT", "8000")))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="manual-labor",
                                description="Nobody reads the appliance manual. A local 4B model does.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="check keys, imports and (optionally) ping one service")
    d.add_argument("--ping", choices=["ollama", "tiger", "ultramarine", "serpapi", "browserbase", "auth0"])
    d.set_defaults(fn=cmd_doctor)

    sub.add_parser("db-init", help="create Tiger Data tables + vector/BM25 indexes").set_defaults(fn=cmd_db_init)

    ad = sub.add_parser("add", help="add an appliance from a plate photo (or --brand/--model, or --pdf)")
    ad.add_argument("--photo"); ad.add_argument("--brand"); ad.add_argument("--model"); ad.add_argument("--pdf")
    ad.set_defaults(fn=cmd_add)

    f = sub.add_parser("fetch", help="drive a support portal with Stagehand (Browserbase if USE_BROWSERBASE=1)")
    f.add_argument("--support-url", required=True); f.add_argument("--model", required=True)
    f.set_defaults(fn=cmd_fetch)

    s = sub.add_parser("search", help="hybrid search one appliance's manual")
    s.add_argument("query"); s.add_argument("--appliance", required=True); s.add_argument("-k", type=int, default=4)
    s.set_defaults(fn=cmd_search)

    c = sub.add_parser("compile", help="Ultramarine reads the manual once and writes the appliance card")
    c.add_argument("--appliance", required=True)
    c.set_defaults(fn=cmd_compile)

    q = sub.add_parser("ask", help="answer a question from the manual, locally")
    q.add_argument("question"); q.add_argument("--appliance", required=True)
    q.add_argument("--model", help="override ANSWER_MODEL (e.g. qwen3.5:4b baseline)")
    q.set_defaults(fn=cmd_ask)

    r = sub.add_parser("remind", help="Temporal: run the worker or schedule an appliance's card")
    r.add_argument("action", choices=["worker", "schedule"]); r.add_argument("--appliance")
    r.set_defaults(fn=cmd_remind)

    w = sub.add_parser("serve", help="family web page on the home Wi-Fi")
    w.add_argument("--host"); w.add_argument("--port", type=int)
    w.set_defaults(fn=cmd_serve)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)
