from app.models.groq_preprocess import process_query
from app.query_processor import determine_function

def query_action_wrapper(text):
    processed_query = process_query(text)
    determine_function(processed_query)
