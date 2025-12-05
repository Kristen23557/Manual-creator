#!/usr/bin/env bash
set -euo pipefail

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Streamlit app..."
streamlit run app.py
