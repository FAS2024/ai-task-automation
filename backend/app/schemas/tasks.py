from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    client_id: str = Field(..., examples=["client-001"])
    workflow_type: str = Field(..., examples=["invoice_processing"])
    payload: Dict[str, Any] = Field(default_factory=dict)


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
