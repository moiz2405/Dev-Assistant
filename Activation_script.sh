#!/bin/bash

# Go to project directory (optional if you are already there)
cd /mnt/d/projects/MYPROJECTS/Dev-Assistant

# Activate virtual environment
source venv/bin/activate

# Export API keys
export GROQ_API_KEY=$(grep '^GROQ_API_KEY=' .env.local | cut -d '=' -f2- | xargs)
export GEMINI_API_KEY=$(grep '^GEMINI_API_KEY=' .env.local | cut -d '=' -f2- | xargs)

# (Optional) Print that environment is ready
echo "✅ Environment ready. Starting Dev-Assistant..."

# Run your main program
python backend/test.py
