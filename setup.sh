#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Export the API keys from .env.local
export GROQ_API_KEY=$(grep '^GROQ_API_KEY=' .env.local | cut -d '=' -f2- | xargs)
export GEMINI_API_KEY=$(grep '^GEMINI_API_KEY=' .env.local | cut -d '=' -f2- | xargs)
# export ELEVENLABS_API_KEY=$(grep '^ELEVENLABS_API_KEY=' .env.local | cut -d '=' -f2- | xargs)

# Optional: Print to verify
echo "Virtual environment activated."
echo "GROQ_API_KEY set"
echo "GEMINI_API_KEY set"
# echo "ELEVENLABS_API_KEY set "

# Don't exec $SHELL unless you have a reason.
# If you want to stay in shell, just leave it.
