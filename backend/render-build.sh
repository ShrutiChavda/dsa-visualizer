#!/usr/bin/env bash
# render-build.sh - Build script for Render.com

set -o errexit

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully"
