#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/src/" && pwd)
PYTHON_FILE="launcher.py"

# Change to the script's directory
cd "$SCRIPT_DIR" || { echo "Directory $SCRIPT_DIR not found"; exit 1; }

# Run the Python file with the provided arguments
python3 "$PYTHON_FILE" "$@"
