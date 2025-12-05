#!/usr/bin/env pwsh
Write-Host "Installing dependencies..."
python -m pip install -r requirements.txt

Write-Host "Starting Streamlit app..."
streamlit run app.py
