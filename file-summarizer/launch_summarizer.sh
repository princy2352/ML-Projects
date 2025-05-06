#!/bin/bash

# Path to your project
PROJECT_PATH="/Users/princypatel/Desktop/file-summarizer"

LOG_FILE="$PROJECT_PATH/summarizer.log"

# Make sure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    open -a Ollama
    # Give Ollama a moment to start
    sleep 3
fi

# Activate the virtual environment and run the tray app
cd "$PROJECT_PATH" && \
source venv/bin/activate && \
python summarizer_tray.py 2>&1 | tee "$LOG_FILE"
