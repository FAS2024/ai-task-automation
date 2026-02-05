from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.services.llm import get_llm


@dataclass
class WorkflowResult:
    task_id: str
    summary: str
    actions: Dict[str, Any]


def run_workflow(task_id: str, payload: Dict[str, Any]) -> WorkflowResult:
    llm = get_llm()
    prompt = (
        "You are an automation agent. Provide a short summary and 3 next actions "
        "for the following workflow payload:\n"
        f"{payload}"
    )
    response = llm.invoke(prompt)

    actions = {
        "action_1": "validate_inputs",
        "action_2": "route_to_pipeline",
        "action_3": "notify_client",
    }
    return WorkflowResult(task_id=task_id, summary=str(response), actions=actions)
