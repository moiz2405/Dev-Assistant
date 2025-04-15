from enum import Enum
class QueryType(str, Enum):
    GITHUB_ACTIONS = "GITHUB_ACTIONS"         
    PROJECT_SETUP = "PROJECT_SETUP"             
    FILE_HANDLING = "FILE_HANDLING"             
    APP_HANDLING = "APP_HANDLING"               
    SUMMARIZER = "SUMMARIZER"                  
    GENERAL_QUERY = "GENERAL_QUERY"
class SubTaskType(str, Enum):
    # GitHub Actions
    LIST_REPOS = "LIST_REPOS"
    CLONE_REPO = "CLONE_REPO"
    CREATE_AND_PUSH = "CREATE_AND_PUSH"

    # Project Setup
    NEW_PROJECT = "NEW_PROJECT"
    EXISTING_PROJECT = "EXISTING_PROJECT"

    # File Handling
    SEARCH_FILE = "SEARCH_FILE"
    OPEN_FILE = "OPEN_FILE"
    CLOSE_FILE = "CLOSE_FILE"

    # App Handling
    OPEN_APP = "OPEN_APP"
    CLOSE_APP = "CLOSE_APP"

    # Summarizer
    SUMMARIZE = "SUMMARIZE"
    ANSWER_QUERY = "ANSWER_QUERY"
    #general 
    GENERAL_QUERY = "GENERAL_QUERY"