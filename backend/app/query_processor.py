# receives user input determines user intent
# if general query or question answers it using a call to chatbot.py else determines the fucntion needed and call it 

from app.functions.app_handling import open_app, close_app
from app.functions.environment_setup import setup_project #takes repo link and target dir as argu, will refine later
from app.functions.file_handler import open_file,list_files_by_type
from app.functions.summarizer import summarize_in_new_window
from app.functions.github_handler import clone_github_repo, list_github_repos, push_folder_to_github
from app.models.query_types import QueryType, SubTaskType

def determine_function(structured_query):
    print(structured_query.type.value)
    print(structured_query.subtask.value)
    print(structured_query.target)
    print(structured_query.path)

    query_type = structured_query.type
    subtask = structured_query.subtask
    target = structured_query.target
    path = structured_query.path

    if query_type == QueryType.APP_HANDLING:
        if subtask == SubTaskType.OPEN_APP:
            open_app(target)
        if subtask == SubTaskType.CLOSE_APP:
            close_app(target)    

    if query_type == QueryType.FILE_HANDLING:
        if subtask == SubTaskType.OPEN_FILE:
            open_file(target,path)
            
    if query_type == QueryType.SUMMARIZER:
        if subtask == SubTaskType.SUMMARIZE:
            summarize_in_new_window(path,target)
    
    if query_type == QueryType.GITHUB_ACTIONS:
        if subtask == SubTaskType.CLONE_REPO:
            clone_github_repo(target,"D://")
            
    # if query_type == QueryType.GENERAL_QUERY:
    # if query_type == QueryType.PROJECT_SETUP:


# def determine_sub_type(structured_query):
    

# def determine_function(structured_query):
#     #for app handling 
#     open_app(app_name)
#     close_app(app_name)
#     #for environment setup 
#     setup_project(repo_link,target_directory)
#     #for file handler
#     search_file(file_name, search_path)
#     open_file(file_path)
#     move_file(file_path, new_location)
    



