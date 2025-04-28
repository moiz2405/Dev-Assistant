# receives user input determines user intent
# if general query or question answers it using a call to chatbot.py else determines the fucntion needed and call it 

from app.functions.github_handler import clone_github_repo, list_github_repos, push_folder_to_github
from app.functions.file_handler import open_file,list_files_by_type
from app.functions.summarizer import summarize_in_new_window
from app.functions.app_handling import open_app, close_app
from app.functions.project_handler.setup_project import setup_existing_project
from app.functions.project_handler.create_project import setup_project

from app.models.query_types import QueryType, SubTaskType

def determine_function(structured_query):
    # print(structured_query)
    # print(structured_query.subtask.value)
    # print(structured_query.target)
    # print(structured_query.path)

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
            clone_github_repo(target,"D://va_projects")
        if subtask == SubTaskType.PUSH_REPO:
            push_folder_to_github(target,"D://va_projects")    
        if subtask == SubTaskType.LIST_REPOS:
            list_github_repos()
            
    if query_type == QueryType.PROJECT_SETUP:
        if subtask == SubTaskType.CREATE_PROJECT:
            setup_project(target,"D://va_projects")
    
    # if query_type == QueryType.GENERAL_QUERY:


# def determine_sub_type(structured_query):
    




