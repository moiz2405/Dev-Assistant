from app.functions.app_handling import close_app

from app.query_processor import determine_function
from app.models.groq_preprocess import process_query
from app.functions.file_handler import open_file

# input = "can u open a pdf names Linux papers from downloads"
# t = 10
# query = process_query(input)
# determine_function(query)

from app.tts.test import VoiceAssistant
def handle_recognized_command(text):
    if text:
        print(f"[MAIN] Recognized: {text}")
        # processed_query = process_query(text)
        # determine_function(processed_query)
        # Call your query processor or route it here
    else:
        print("[MAIN] Nothing recognized.")
assistant = VoiceAssistant(hotword="jarvis", record_duration=4,on_recognized=handle_recognized_command)
assistant.start_hotword_listener()
# while(t):
#     t = t-1
# open_file(input)
# close_app(input)
