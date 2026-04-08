from uuid import uuid4

import redis.asyncio as redis
from celery.result import AsyncResult
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db, require_admin
from app.core.limiter import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.models import TaskRun, User
from app.schemas.auth import TokenResponse, UserCreateRequest
from app.schemas.tasks import TaskCreateRequest, TaskCreateResponse, TaskStatusResponse
from app.services.event_bus import get_event_bus
from app.tasks.celery_app import celery_app
from app.tasks.tasks import process_workflow

router = APIRouter(tags=["core"])
settings = get_settings()


@router.get("/me", tags=["auth"])
def me(user: User = Depends(get_current_user)) -> dict:
    return {"email": user.email, "role": user.role}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}


@router.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }


@router.get("/health/ready")
async def readiness() -> dict:
    redis_ok = None
    if settings.redis_url:
        try:
            client = redis.from_url(settings.redis_url)
            await client.ping()
            await client.close()
            redis_ok = True
        except Exception:
            redis_ok = False
    return {"status": "ready", "redis": redis_ok}


@router.post("/auth/register", response_model=TokenResponse, tags=["auth"])
@limiter.limit("5/minute")
def register_user(
    request: Request,
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email, user.role)
    return TokenResponse(access_token=token)


@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
@limiter.limit("10/minute")
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email, user.role)
    return TokenResponse(access_token=token)


@router.post("/tasks", response_model=TaskCreateResponse)
@limiter.limit("30/minute")
def create_task(
    request: Request,
    payload: TaskCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TaskCreateResponse:
    task_id = str(uuid4())
    process_workflow.apply_async(args=(task_id, payload.model_dump()), task_id=task_id)
    db.add(
        TaskRun(
            task_id=task_id,
            client_id=payload.client_id,
            workflow_type=payload.workflow_type,
            status="queued",
        )
    )
    db.commit()
    return TaskCreateResponse(task_id=task_id, status="queued")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    status = result.status.lower()
    payload = result.result if result.successful() else None
    run = db.query(TaskRun).filter(TaskRun.task_id == task_id).first()
    if run and payload:
        run.status = status
        run.summary = payload.get("summary")
        db.commit()
    return TaskStatusResponse(task_id=task_id, status=status, result=payload)


@router.get("/admin/task-runs", tags=["admin"])
def list_task_runs(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    rows = db.query(TaskRun).order_by(TaskRun.created_at.desc()).limit(50).all()
    return [
        {
            "task_id": row.task_id,
            "client_id": row.client_id,
            "workflow_type": row.workflow_type,
            "status": row.status,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.websocket("/ws/updates")
async def websocket_updates(socket: WebSocket) -> None:
    await socket.accept()
    event_bus = get_event_bus()
    await event_bus.connect()
    try:
        if not event_bus.is_active:
            await socket.send_json(
                {
                    "status": "noop",
                    "detail": "Redis not configured or unavailable.",
                }
            )
            while True:
                await socket.receive_text()
        else:
            async for message in event_bus.subscribe():
                await socket.send_json(message)
    except WebSocketDisconnect:
        pass
    finally:
        await event_bus.disconnect()
