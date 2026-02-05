## Contributing

Thanks for your interest in contributing. This project is built as a production‑ready
portfolio example; the guidelines below keep the codebase consistent and reliable.

## Workflow
- Create a feature branch from `main`
- Keep changes focused and small
- Update docs/tests when behavior changes

## Quality checks
```bash
cd backend
.\.venv\Scripts\activate
ruff check .
pytest
```

## Commit style
- Use clear, descriptive commit messages
- Prefer present tense: “Add rate limit middleware”

## Security
- Do not commit secrets
- Use `backend/env.sample.txt` for configuration examples
