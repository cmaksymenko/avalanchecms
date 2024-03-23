#!/bin/sh
set -e

echo "Running Avalanche CLI tests..."

if ! command -v python3 > /dev/null 2>&1; then
    echo "Python could not be found. Please install Python."
    exit 1
fi

if ! command -v pip3 > /dev/null 2>&1; then
    echo "pip could not be found. Please install pip."
    exit 1
fi

if pip3 list | grep -F pytest > /dev/null 2>&1; then
    echo "pytest is already installed."
else
    echo "pytest is not installed. Installing pytest..."
    if pip3 install pytest ; then
        echo "pytest installed successfully."
    else
        echo "Failed to install pytest."
        exit 1
    fi
fi

if pip3 install -r requirements.txt ; then
    echo "Requirements installed successfully."
else
    echo "Failed to install requirements."
    exit 1
fi

if pytest ; then
    echo "Tests for Avalanche CLI completed successfully."
else
    echo "Tests for Avalanche CLI failed."
    exit 1
fi
