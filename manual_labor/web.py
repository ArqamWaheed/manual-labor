"""The family page: pick an appliance, ask, get steps + page. Runs on the home Wi-Fi."""
from __future__ import annotations

from importlib import resources


def create_app():
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    app = FastAPI(title="Manual Labor")

    class Ask(BaseModel):
        appliance_id: str
        question: str

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return resources.files("manual_labor").joinpath("static/index.html").read_text()

    @app.get("/api/appliances")
    def appliances() -> list[dict]:
        from manual_labor import store

        with store.connect() as c:
            rows = c.execute("SELECT id, brand, model, kind FROM appliances ORDER BY kind, brand").fetchall()
        return [dict(zip(("id", "brand", "model", "kind"), r)) for r in rows]

    @app.post("/api/ask")
    def ask(body: Ask) -> dict:
        from manual_labor import store
        from manual_labor.answer import answer

        pages = store.search_hybrid(body.appliance_id, body.question)
        a = answer(body.question, pages)
        return a.__dict__

    # TODO: POST /api/plate (photo upload -> plate.read_plate -> add pipeline), behind the home network only.
    return app


def serve(host: str, port: int) -> None:
    import uvicorn

    uvicorn.run(create_app(), host=host, port=port)
