#!/bin/sh
set -e

echo "Running Avalanche CLI tests..."

# Select python3 or python; exit if missing
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v python > /dev/null 2>&1; then
    PYTHON_CMD=python    
else
    echo "Python could not be found. Please install Python."
    exit 1
fi

# Ensure Python 3 is available; exit if not
if command -v python3 > /dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v python > /dev/null 2>&1 && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD=python
else
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

echo "Using $PYTHON_CMD and $PIP_CMD"

# Check for pytest; install if missing, exit on failure
if $PIP_CMD list | grep -F pytest > /dev/null 2>&1; then
    echo "pytest is already installed."
else
    echo "pytest is not installed. Installing pytest..."
    if $PIP_CMD install pytest ; then
        echo "pytest installed successfully"
    else
        echo "Failed to install pytest"
        exit 1
    fi
fi

# Install requirements from file; exit if failure
if $PIP_CMD install -r requirements.txt ; then
    echo "Requirements installed successfully"
else
    echo "Failed to install requirements"
    exit 1
fi

# Run pytest for Avalanche CLI; exit if tests fail
if pytest ; then
    echo "Tests for Avalanche CLI completed successfully"
else
    echo "Tests for Avalanche CLI failed"
    exit 1
fi
