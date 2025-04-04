from enum import Enum
from typing import Iterator
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq

class QueryType(str, Enum):
    GITHUB_ACTIONS = "GITHUB_ACTIONS"         
    PROJECT_SETUP = "PROJECT_SETUP"             
    FILE_HANDLING = "FILE_HANDLING"             
    APP_HANDLING = "APP_HANDLING"               
    SUMMARIZER = "SUMMARIZER"                  

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
            "   - If no folder is specified, default to the 'Documents' directory (e.g., 'C:\\Documents\\')."
            "Formatting Rules:"
            "- Always use single backslashes (\\) between directories."
            "- Ensure the full absolute path (starting with drive letter) is returned."
            "Examples:"
            "- 'Open report.pdf' → path: 'C:\\Documents\\report.pdf'"
            "- 'Set up a Next.js project in D drive' → path: 'D:\\new_folder' or 'D:\\NextJsApp' (if name found)"
            "- 'Save it in my_projects' → path: 'C:\\my_projects' (if no drive specified)"
        )
    )

def boost_prompt(prompt: str) -> str:
    summarizer_keywords = [
        "summarize", "answer from", "explain from", "read from", "understand from", 
        "questions from", "query from", "explain this pdf", "tell from", "pdf context"
    ]
    lowered = prompt.lower()
    if any(kw in lowered for kw in summarizer_keywords):
        return "[TASK:SUMMARIZER] " + prompt
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
        ),
        markdown=True,
        response_model=QueryProcessor,
    )

def main_loop():
    agent = get_agent()
    while True:
        try:
            prompt = input(">>> ")
            if prompt.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            boosted = boost_prompt(prompt)
            agent.print_response(boosted, stream=True)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def stream_loop():
    agent = get_agent()
    while True:
        prompt = input(">>> ")
        boosted = boost_prompt(prompt)
        output: Iterator[RunResponse] = agent.run(boosted, stream=True)
        for curr in output:
            print(curr.content)

if __name__ == "__main__":
    main_loop()
