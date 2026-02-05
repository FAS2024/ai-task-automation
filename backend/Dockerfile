FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY scripts ./scripts

RUN chmod +x /app/scripts/entrypoint.sh

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
