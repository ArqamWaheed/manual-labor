"""Stagehand drives brand support portals (local Chrome while developing, Browserbase for real runs).

Browserbase Free = 1 browser-hour total, 15 min/session, no captcha solving. Close sessions in finally.
API per https://docs.stagehand.dev/v4/first-steps/quickstart.md and .../configuration/browser.md
"""
from __future__ import annotations

import time

from manual_labor.config import settings
from manual_labor.costs import log_run


async def _launch():
    from stagehand import browserbase, local_browser

    s = settings()
    if s.use_browserbase:
        return await browserbase.launch(api_key=s.browserbase_key)
    return await local_browser.launch()


async def _model():
    """First-class provider string (e.g. groq/openai/gpt-oss-120b), or a bring-your-own-LLM callback."""
    s = settings()
    if s.stagehand_model != "local":
        return s.stagehand_model
    # TODO: callback to local Ollama (OpenAI-compatible). Must return LLMStructuredGenerateResult with
    #       structured_content; see the 'Custom models' section of the Stagehand models doc.
    raise NotImplementedError("local Stagehand callback not written yet")


async def fetch_manual_links(support_url: str, model_number: str) -> list[dict]:
    from pydantic import BaseModel
    from stagehand import Stagehand

    class PdfLink(BaseModel):
        title: str
        url: str

    class PdfLinks(BaseModel):
        links: list[PdfLink]

    s = settings()
    t0 = time.perf_counter()
    browser = await _launch()
    try:
        sh = await Stagehand.create(browser=browser, model=await _model(),
                                    model_api_key=s.stagehand_model_key or None)
        try:
            page = (await browser.context.pages())[0]
            await page.goto(support_url)
            await sh.act(f"Type the model number {model_number} into the product or model search box and submit")
            await sh.act("Open the result that matches the model number exactly")
            await sh.act("Open the Manuals, Documents or Downloads section")
            res = await sh.extract("List every PDF manual link on this page with its title", PdfLinks)
            links = [l.model_dump() for l in res.data.links]
        finally:
            await sh.close()
    finally:
        await browser.close()
    log_run("browser", f"portal:{model_number}", cloud=int(s.use_browserbase),
            seconds=round(time.perf_counter() - t0, 1), links=len(links))
    # TODO: record Stagehand cache hits (run 1 vs run 2 LLM calls) for the post; see best-practices/caching.
    return links


async def fill_service_form(form_url: str, fields: dict[str, str]) -> object:
    """Fill a brand's service-request form and STOP before submit. Returns the open session for approve.py."""
    # TODO (stretch, Auth0): act() each field, screenshot, then approve.request_approval(); click Submit
    #       only if it returns True. Test against mock/service_form.html first.
    raise NotImplementedError
