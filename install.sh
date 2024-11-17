#!/bin/bash

# Install the necessary dependencies
echo "Checking if dependencies are installed..."

# Check if telethon is installed
pip show telethon > /dev/null
if [ $? -eq 1 ]; then
    echo "Installing telethon..."
    pip install telethon
fi

# Check if tgcrypto is installed
pip show tgcrypto > /dev/null
if [ $? -eq 1 ]; then
    echo "Installing tgcrypto..."
    pip install tgcrypto
fi

# Check if cryptg is installed
pip show cryptg > /dev/null
if [ $? -eq 1 ]; then
    echo "Installing cryptg..."
    pip install cryptg
fi

echo "All dependencies are installed!"
