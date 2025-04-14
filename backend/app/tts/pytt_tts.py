import pyttsx3
from collections import defaultdict

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices_by_language = self._organize_voices()
        
    def _organize_voices(self):
        voices = defaultdict(list)
        for voice in self.engine.getProperty('voices'):
            # Clean up language codes (take first part before hyphen)
            lang_code = voice.languages[0].split('-')[0] if voice.languages else 'unknown'
            voices[lang_code].append({
                'id': voice.id,
                'name': voice.name,
                'gender': 'female' if 'female' in voice.id.lower() else 'male',
                'full_lang': voice.languages[0] if voice.languages else 'unknown'
            })
        return dict(voices)
    
    def list_voices(self, language_code=None):
        """List available voices, optionally filtered by language code"""
        if language_code:
            if language_code in self.voices_by_language:
                print(f"\nVoices for {language_code}:")
                for i, voice in enumerate(self.voices_by_language[language_code]):
                    print(f"{i}: {voice['name']} ({voice['gender']}) - {voice['full_lang']}")
            else:
                print(f"No voices found for language code: {language_code}")
        else:
            print("\nAvailable languages:")
            for lang_code in sorted(self.voices_by_language.keys()):
                count = len(self.voices_by_language[lang_code])
                print(f"{lang_code}: {count} voice{'s' if count != 1 else ''}")
    
    def speak(self, text, language_code='en', voice_index=0):
        """Speak text using specified language and voice index"""
        try:
            if language_code not in self.voices_by_language:
                raise ValueError(f"Language {language_code} not available")
                
            voices = self.voices_by_language[language_code]
            if not voices:
                raise ValueError(f"No voices available for {language_code}")
                
            if voice_index >= len(voices):
                voice_index = 0  # Fallback to first voice
                
            voice_id = voices[voice_index]['id']
            self.engine.setProperty('voice', voice_id)
            self.engine.setProperty('rate', 175)  # Moderate speed
            self.engine.setProperty('volume', 0.9)  # 90% volume
            
            print(f"Speaking with: {voices[voice_index]['name']}")
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Error in TTS: {str(e)}")
            # Fallback to default voice
            self.engine.say(text)
            self.engine.runAndWait()

# Usage example
if __name__ == "__main__":
    tts = TTSEngine()
    
    # List all available languages
    tts.list_voices()
    
    # List voices for specific language
    tts.list_voices('en')  # English
    tts.list_voices('es')  # Spanish
    
    # Speak with specific language and voice
    tts.speak("Hello, I'm your AI assistant", 'en', 0)
    tts.speak("Hola, soy tu asistente de IA", 'es', 0)