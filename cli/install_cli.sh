#!/bin/sh
set -e

#!/bin/sh

echo "Starting installation of Avalanche CLI..."

if ! command -v python3 > /dev/null 2>&1; then
    echo "Python could not be found. Please install Python."
    exit 1
fi

if ! command -v pip3 > /dev/null 2>&1; then
    echo "pip could not be found. Please install pip."
    exit 1
fi

if pip3 install --editable . ; then
    echo "Avalanche CLI has been installed successfully."
else
    echo "Installation of Avalanche CLI failed."
    exit 1
fi