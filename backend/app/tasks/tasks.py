from __future__ import annotations

from typing import Any, Dict

from app.db import SessionLocal
from app.models import TaskRun
from app.services.event_bus import get_event_bus
from app.services.workflow import run_workflow
from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.process_workflow")
def process_workflow(task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    result = run_workflow(task_id, payload)
    payload = {
        "task_id": task_id,
        "summary": result.summary,
        "actions": result.actions,
        "status": "completed",
    }

    db = SessionLocal()
    try:
        run = db.query(TaskRun).filter(TaskRun.task_id == task_id).first()
        if run:
            run.status = "completed"
            run.summary = payload["summary"]
            db.commit()
    finally:
        db.close()

    event_bus = get_event_bus()
    if event_bus:
        try:
            import asyncio

            async def _publish() -> None:
                await event_bus.connect()
                await event_bus.publish(payload)
                await event_bus.disconnect()

            asyncio.run(_publish())
        except RuntimeError:
            # Already inside an event loop (unlikely in Celery), just skip.
            pass

    return payload
