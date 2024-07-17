#!/bin/bash

# Directory containing the files
DIRECTORY="./components"

# Text to prepend
TEXT='"use client";'

process_file() {
  local FILE=$1
  TEMP_FILE=$(mktemp)

  echo "$TEXT" > "$TEMP_FILE"

  cat "$FILE" >> "$TEMP_FILE"

  mv "$TEMP_FILE" "$FILE"
}

export -f process_file
export TEXT

# Find .tsx files and process them
find "$DIRECTORY" -type f -name "*.tsx" -exec bash -c 'process_file "$0"' {} \;

echo "Done"
