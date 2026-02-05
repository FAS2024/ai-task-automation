# Architecture Overview

```mermaid
flowchart LR
  Client[API Client / UI] -->|HTTP| API[FastAPI API]
  Client -->|WebSocket| WS[WebSocket / Updates]
  API -->|enqueue| Celery[Celery Worker]
  Celery -->|run workflow| LLM[LangChain + GPT-4 / Mock]
  API <--> Redis[(Redis)]
  Celery <--> Redis
  API <--> DB[(Postgres)]
  WS <--> Redis
```

## Key Components
- **FastAPI**: REST + WebSocket entrypoint, auth, rate limiting, readiness.
- **Celery**: async workflow execution.
- **Redis**: broker + pubsub for realtime updates.
- **Postgres**: persistence for users and task runs.
- **LangChain + GPT-4**: optional LLM; mock used if no key.
