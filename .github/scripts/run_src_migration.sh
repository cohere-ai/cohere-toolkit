#!/bin/bash
cd $SSH_PROJECT_DIR
git pull
source .venv/bin/activate
alembic -c src/backend/alembic.ini upgrade head
echo "Migration complete"
