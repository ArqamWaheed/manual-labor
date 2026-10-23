"""Temporal: one ApplianceCare workflow per maintenance task, with month-long durable timers.

Run the dev server:  temporal server start-dev --db-filename .temporal.db
Run the worker:      python -m manual_labor remind worker
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta

try:
    from temporalio import activity, workflow
except ImportError:  # keep `--help` working without the temporal extra
    activity = workflow = None  # type: ignore[assignment]


@dataclass
class CareTask:
    appliance_id: str
    task: str
    every_days: int
    page: int


if workflow is not None:

    @activity.defn
    async def notify(t: CareTask) -> str:
        from manual_labor.config import settings
        import urllib.request

        topic = settings().ntfy_topic
        msg = f"{t.task} (manual p. {t.page})".encode()
        urllib.request.urlopen(urllib.request.Request(f"https://ntfy.sh/{topic}", data=msg), timeout=15)  # noqa: S310
        return "sent"

    @workflow.defn
    class ApplianceCare:
        def __init__(self) -> None:
            self.done = False
            self.snooze_days = 0

        @workflow.signal
        def mark_done(self) -> None:
            self.done = True

        @workflow.signal
        def snooze(self, days: int) -> None:
            self.snooze_days = days

        @workflow.run
        async def run(self, t: CareTask) -> None:
            while True:
                await workflow.sleep(timedelta(days=t.every_days))
                self.done = False
                while not self.done:
                    await workflow.execute_activity(notify, t, start_to_close_timeout=timedelta(seconds=30))
                    try:  # wait up to 3 days for "done", then nag again
                        await workflow.wait_condition(lambda: self.done or self.snooze_days > 0,
                                                      timeout=timedelta(days=3))
                    except asyncio.TimeoutError:
                        continue
                    if self.snooze_days:
                        days, self.snooze_days = self.snooze_days, 0
                        await workflow.sleep(timedelta(days=days))
                # TODO: continue_as_new every N cycles to keep history small.


async def run_worker() -> None:
    from temporalio.client import Client
    from temporalio.worker import Worker

    from manual_labor.config import settings

    s = settings()
    client = await Client.connect(s.temporal_address, namespace=s.temporal_namespace)
    await Worker(client, task_queue=s.temporal_queue, workflows=[ApplianceCare], activities=[notify]).run()


async def schedule_card(appliance_id: str, card: dict) -> list[str]:
    from temporalio.client import Client

    from manual_labor.config import settings

    s = settings()
    client = await Client.connect(s.temporal_address, namespace=s.temporal_namespace)
    ids = []
    for m in card.get("maintenance", []):
        wid = f"care-{appliance_id}-{m['task'][:40]}".replace(" ", "-").lower()
        await client.start_workflow(ApplianceCare.run, CareTask(appliance_id, m["task"], m["every_days"], m["page"]),
                                    id=wid, task_queue=s.temporal_queue)
        ids.append(wid)
    return ids
