#!/usr/bin/env bash

# Ensure compatibility with both bash and zsh
if [ -n "$ZSH_VERSION" ]; then
    # ZSH-specific settings
    setopt SH_WORD_SPLIT
    setopt KSH_ARRAYS
fi

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Determine Python command to use
PYTHON_CMD="python"
if ! command -v python &> /dev/null && command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Pass all arguments to the Python script
if [ -n "$ZSH_VERSION" ]; then
    # ZSH-specific path handling
    script_dir="${0:a:h}"
else
    # Bash path handling
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

python_script="${script_dir}/release.py"

# Check if the Python script exists
if [ ! -f "$python_script" ]; then
    echo "Error: Python script not found at $python_script"
    exit 1
fi

# Run the Python script with all arguments
exec "$PYTHON_CMD" "$python_script" "$@"