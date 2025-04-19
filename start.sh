#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Export the API key from your .env file
export GROQ_API_KEY=$(grep GROQ_API_KEY .env.local | cut -d '=' -f2)
export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env.local | cut -d '=' -f2)
export ELEVENLABS_API_KEY_API_KEY=$(grep ELEVENLABS_API_KEY .env.local | cut -d '=' -f2)


# Optional: Run your Python script after this
echo "Virtual environment activated."
exec "$SHELL"  # Keeps you in the activated shell
