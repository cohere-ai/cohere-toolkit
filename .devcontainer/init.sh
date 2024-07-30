#!/bin/bash

# Check if .env file exists or needs to be created
if [ ! -f .env ]; then
    # Check if .env-template exists and copy it to .env
    if [ -f .env-template ]; then
        cp .env-template .env
    else
        echo "Error: .env-template file not found. Please create or copy it to the current directory."
    fi
fi

# Get and replace CODESPACE_NAME in .env file if it exists
if [ -f .env ]; then
    CODESPACE_NAME=$(eval echo "$CODESPACE_NAME")
    sed -i "s|NEXT_PUBLIC_API_HOSTNAME=http://localhost:8000|NEXT_PUBLIC_API_HOSTNAME=https://$CODESPACE_NAME-8000.app.github.dev|g" .env
fi

port=8000
visibility=public
max_attempts=5
backoff_seconds=2

# Check gh command and its output
gh_output=$(gh --version 2>&1)
gh_exit_code=$?

if [ $gh_exit_code -ne 0 ]; then
    echo "Error: 'gh' command not found. Please install GitHub CLI."
    exit 1
fi

# Update port visibility with exponential backoff
attempt=1
echo "Updating port $port visibility to $visibility (attempt $attempt/$max_attempts)"
while true; do
    if gh codespace ports visibility $port:$visibility -c $CODESPACE_NAME; then
        break # Exit the loop if successful
    fi

    echo "Error: Failed to update port visibility. Retrying in $backoff_seconds seconds..."
    sleep $backoff_seconds
    backoff_seconds=$((backoff_seconds * 2)) # Double the backoff time for each retry
    attempt=$((attempt + 1))

    if [ $attempt -gt $max_attempts ]; then
        echo "Exceeded maximum attempts. Failed to update port visibility."
        exit 1
    fi
done

echo "Set up complete. Add API key(s) to your .env file and then run \`make up\`."
