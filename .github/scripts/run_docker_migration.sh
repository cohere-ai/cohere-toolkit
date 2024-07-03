#!/bin/bash
cd $SSH_PROJECT_DIR
git pull
make migrate
echo "Migration complete"
