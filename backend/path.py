from app.functions.app_handling import close_app

from app.query_processor import determine_function
from app.models.groq_preprocess import process_query
from app.functions.file_handler import open_file

# input = "can u open a pdf names Linux papers from downloads"
# t = 10
# query = process_query(input)
# determine_function(query)

from app.tts.test import VoiceAssistant
assistant = VoiceAssistant()
assistant.start_hotword_listener()
# while(t):
#     t = t-1
# open_file(input)
# close_app(input)
