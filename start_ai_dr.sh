#!/bin/bash

PROJECT_DIR="/home/neha/AI_Disaster-Management"
PYTHON="$PROJECT_DIR/.venv/bin/python"

cd "$PROJECT_DIR" || exit 1

exec "$PYTHON" app.py
