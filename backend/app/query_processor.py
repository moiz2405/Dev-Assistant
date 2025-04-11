# receives user input determines user intent
# if general query or question answers it using a call to chatbot.py else determines the fucntion needed and call it 
# determines user intent
# call required function to take action
# types of actions or functions to create 
# 1)project / environment setup - new or existing 
# 2) file handling - search or open a file
# 3) apps - open or close an app
# 4) pdf summarizer - summarizes and pdf 
# 5) research on a topic 
# 6)general query or question

from app.functions.app_handling import open_app, close_app
from app.functions.environment_setup import setup_project #takes repo link and target dir as argu, will refine later
from app.functions.file_handler import search_file, open_file, move_file, list_files_by_type


def determine_type(structured_query):
    if(structured_query.type = )

def determine_sub_type(structured_query):
    

def determine_function(structured_query):
    #for app handling 
    open_app(app_name)
    close_app(app_name)
    #for environment setup 
    setup_project(repo_link,target_directory)
    #for file handler
    search_file(file_name, search_path)
    open_file(file_path)
    move_file(file_path, new_location)
    



