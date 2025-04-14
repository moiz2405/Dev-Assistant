import pyttsx3

def speak_as_butler(text):
    engine = pyttsx3.init()

    # Butler-style configuration
    engine.setProperty('rate', 150)  # Moderate speed
    engine.setProperty('volume', 0.9)  # High volume

    voices = engine.getProperty('voices')
    
    # Try to use a deeper male voice if available
    for voice in voices:
        if 'english' in voice.name.lower() and ('male' in voice.name.lower() or 'david' in voice.name.lower()):
            engine.setProperty('voice', voice.id)
            break

    # Preprompt Butler Style
    prompt = "Certainly, sir. " + text
    engine.say(prompt)
    engine.runAndWait()

# Example usage
speak_as_butler("The task has been initiated. I shall notify you upon completion.")
