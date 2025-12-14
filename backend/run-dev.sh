#!/bin/bash
# Run backend development server on port 8000

cd "$(dirname "$0")"
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

