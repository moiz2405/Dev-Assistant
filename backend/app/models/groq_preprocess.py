#takes user queries and return structered json output , determines 
# query_type, sub_query, path, target

from enum import Enum
from typing import Iterator
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from pathlib import Path
import platform
import os
import getpass
import diskcache
cache = diskcache.Cache(".query_cache")

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

class QueryProcessor(BaseModel):
    type: QueryType = Field(
        ...,
        description=(
            "Correctly determine the type of query from:\n"
            "1) GITHUB_ACTIONS - List repos, clone repo & setup, make/push to repo.\n"
            "2) PROJECT_SETUP - Setup a new/existing project environment (like Next.js, Flask).\n"
            "3) FILE_HANDLING - Search, open, or close a file.\n"
            "4) APP_HANDLING - Open or close an application.\n"
            "5) SUMMARIZER - Summarize or answer questions using a given PDF/document."
        )
    )
    subtask: SubTaskType = Field(
        ...,
        description=(
            "The specific sub-action within the main type:\n"
            "- GITHUB_ACTIONS: LIST_REPOS, CLONE_REPO, CREATE_AND_PUSH\n"
            "- PROJECT_SETUP: NEW_PROJECT, EXISTING_PROJECT\n"
            "- FILE_HANDLING: SEARCH_FILE, OPEN_FILE, CLOSE_FILE\n"
            "- APP_HANDLING: OPEN_APP, CLOSE_APP\n"
            "- SUMMARIZER: SUMMARIZE, ANSWER_QUERY"
        )
    )
    target: str = Field(
        ...,
        description=(
            "Main target of the query:\n"
            "- FILE_HANDLING: file name with extension (e.g., report.pdf, notes.txt)\n"
            "- APP_HANDLING: valid app name (e.g., Chrome, VS Code, WhatsApp)\n"
            "- GITHUB_ACTIONS: repo name (e.g., chat-bot)\n"
            "- PROJECT_SETUP: project type or name (e.g., Flask, Next.js)\n"
            "- SUMMARIZER: filename (e.g., summary.pdf)"
        )
    )
    path: str = Field(
        ...,
        description=(
           "Determine the correct full Windows-style path for the file or folder referenced in the query."
            "Guidelines:"
            "1) If the user provides a path (e.g., 'C:\\my_file' or 'D:\\Projects\\MyApp'), use it directly."
            "2) If the user wants to create a new folder or set up a new project:"
            "   - Extract the folder/project name from the query, if specified."
            "   - Place it under a suitable drive (prefer 'D:\\' if mentioned, otherwise default to 'C:\\')."
            "   - Use 'C:\\new_folder' or 'D:\\new_folder' as a fallback if no name is provided."
            "3) For file-related actions (like SEARCH_FILE, OPEN_FILE, etc.):"
            "   - If no folder is specified, default to the 'Documents\\' directory (e.g., 'Documents\\')."
            "Formatting Rules:"
            "- Always use single backslashes (\\) between directories."
            "- Ensure the full absolute path (starting with drive letter) is returned."
            "Examples:"
            "- 'Open report.pdf' → path: 'C:\\Downloads\\report.pdf'"
            "- 'Set up a Next.js project in D drive' → path: 'D:\\new_folder' or 'D:\\NextJsApp' (if name found)"
            "- 'Save it in my_projects' → path: 'C:\\my_projects' (if no drive specified)"
        )
    )

def boost_prompt(prompt: str) -> str:
    summarizer_keywords = [
        "summarize", "answer from", "explain from", "read from", "understand from", 
        "questions from", "query from", "explain this pdf", "tell from", "pdf context"
    ]
    general_keywords = [
        "weather", "who is", "capital of", "how many", "when was", "current", "tell me about",
        "time in", "president", "prime minister", "fun fact", "general knowledge"
    ]

    path_boosts = {
        "downloads": " [HINT_PATH: C:\\Users\\km866\\Downloads\\] ",
        "documents": " [HINT_PATH: C:\\Users\\km866\\Documents\\] ",
        "desktop": " [HINT_PATH: C:\\Users\\km866\\Desktop\\] ",
        "d drive": " [HINT_PATH: D:\\] ",
        "c drive": " [HINT_PATH: C:\\] ",
        "my projects": " [HINT_PATH: C:\\my_projects\\] ",
    }

    lowered = prompt.lower()

    # General knowledge route
    if any(kw in lowered for kw in general_keywords):
        return "[TASK:GENERAL_QUERY] " + prompt

    # Summarizer route
    if any(kw in lowered for kw in summarizer_keywords):
        return "[TASK:SUMMARIZER] " + prompt

    # Add path hint if any matched
    for key, path_hint in path_boosts.items():
        if key in lowered:
            prompt = f"{prompt} {path_hint}"
            break

    return prompt


def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a smart query processor. Your job is to translate natural language user queries "
            "into structured data with fields: type, subtask, target, and path.\n"
            "- Recognize summarization or document-based queries as SUMMARIZER.\n"
            "- Classify GitHub-related tasks as GITHUB_ACTIONS.\n"
            "- Be precise with subtask selection."
            "- Be precise with subtask selection.\n"
            "- Return the path all in lower case"
            "- If the query mentions a file (e.g., 'pdf named college', 'from my file xyz'), extract the filename "
            "and ensure it ends with '.pdf', DONT EVER GIVE SPACES BETWEEN NAMES IN A FILE LIKE FILE FILE IS NAMES collegenotes.pdf let it.\n"
            "- Construct the absolute file path in the format: C:\\\\Users\\\\km866\\\\Downloads\\\\<filename>.pdf\n"
            "- Set 'target' as the full filename with extension, and 'path' as the complete path to that file.\n"
            "- Preserve the extension (e.g., .pdf) since it is needed for file access or processing." 
        ),
        markdown=True,
        response_model=QueryProcessor,
    )


def get_default_download_path(filename: str) -> str:
    user = getpass.getuser()
    return f"C:\\Users\\km866\\Downloads\\{filename}"

    
# Move this outside for reuse
AGENT_MAIN = get_agent()
AGENT_GENERAL = Agent(model=Groq(id="llama-3.3-70b-versatile"))

def process_query(prompt: str) -> QueryProcessor:
    boosted_prompt = boost_prompt(prompt)

    if "[TASK:GENERAL_QUERY]" in boosted_prompt:
        general_response = AGENT_GENERAL.run(boosted_prompt.replace("[TASK:GENERAL_QUERY] ", ""), stream=False)
        return QueryProcessor(
            type=QueryType.GENERAL_QUERY,
            subtask=SubTaskType.GENERAL_QUERY,
            target=general_response.content.strip(),
            path=""
        )

    response = AGENT_MAIN.run(boosted_prompt, stream=False)
    return response.content

def cached_process_query(prompt: str) -> QueryProcessor:
    normalized_prompt = " ".join(prompt.strip().lower().split())
    if normalized_prompt in cache:
        print("[CACHE HIT]")
        return cache[normalized_prompt]
    else:
        print("[CACHE MISS]")
    result = process_query(prompt)
    cache[normalized_prompt] = result
    return result