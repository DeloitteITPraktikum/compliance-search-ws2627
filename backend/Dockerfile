FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "compliance_search.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
