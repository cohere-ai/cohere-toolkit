#!/bin/bash

if [ "$DEBUGGER_IDE" = "vscode" ]; then
    python -m debugpy --listen 0.0.0.0:5678 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 300
elif [ "$DEBUGGER_IDE" = "pycharm" ]; then
    python src/backend/pycharm_debug_main.py
else
    echo "Debugger IDE is not set to a recognized value. Fix the value of DEBUGGER_IDE."
fi