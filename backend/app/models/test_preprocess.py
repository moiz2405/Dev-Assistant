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
# from query_types import QueryType, SubTaskType
from app.models.query_types import QueryType,SubTaskType,PathType
cache = diskcache.Cache(".query_cache")


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
    path: PathType = Field(
        ...,
        description=(
           "Determine the correct path directory from the user query"
           "- from DOWNLOADS DOCUMENTS DESKTOP D_DRIVE, C_DRIVE"
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
        "documents": " [HINT_PATH: Documents\\] ",
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
            "- Always return Windows-style paths starting with capital drive letters (e.g., C:\\, D:\\)."
            "- Capitalize the drive letter in the path (e.g., C:\\Users\\...)."
            "- If the query mentions a file (e.g., 'pdf named college', 'from my file xyz'), extract the filename "
            "- Construct the absolute file path in the format: C:\\Users\\km866\\Downloads\\<filename> with extension\n"
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
        print(cache[normalized_prompt])
        return cache[normalized_prompt]
    else:
        print("[CACHE MISS]")

    result = process_query(prompt)
    cache[normalized_prompt] = result
    print(result)
    return result
8