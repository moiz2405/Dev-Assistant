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
from app.models.query_types import QueryType,SubTaskType
cache = diskcache.Cache(".query_cache")


class QueryProcessor(BaseModel):
    type: QueryType = Field(
        ...,
        description=(
            "Correctly determine the type of query from:\n"
            "1) GITHUB_ACTIONS - LIST_REPOS, PUSH_REPO, CLONE_REPO.\n"
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
            "- GITHUB_ACTIONS: LIST_REPOS, CLONE_REPO, PUSH_REPO\n"
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
            "Determine the correct full Windows-style path for the file or folder referenced in the query.\n\n"
            "Guidelines:\n"
            "- Use 'D:\\' for GITHUB_ACTIONS and PROJECT_SETUP (fallback to 'C:\\' if 'D:\\' is not mentioned).\n"
            "- If the query includes terms like 'create' or 'new':\n"
            "  - Extract the folder/project name from the query if specified.\n"
            "  - Place it under the preferred drive ('D:\\' if mentioned, otherwise 'C:\\').\n"
            "  - Use 'D:\\new_folder' or 'C:\\new_folder' as a fallback if no name is found.\n"
            "- If the user provides a full path (e.g., 'C:\\my_file' or 'D:\\Projects\\MyApp'), use it directly.\n"
            "- For file-related actions (e.g., SEARCH_FILE, OPEN_FILE):\n"
            "  - If no folder is specified, default to 'Documents\\'.\n\n"
            "Formatting Rules:\n"
            "- Always use single backslashes (\\) between directories.\n"
            "- Paths should follow Windows format using capital drive letters.\n"
            "- Return absolute paths where applicable.\n\n"
            "Examples:\n"
            "- 'Open report.pdf' → path: 'Documents\\report.pdf'\n"
            "- 'Set up a Next.js project in D drive' → path: 'D:\\NextJsApp' (if name extracted) or 'D:\\new_folder'\n"
            "- 'Save it in my_projects' → path: 'C:\\my_projects' (if no drive is specified)"
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

    lowered = prompt.lower()

    # General knowledge route
    if any(kw in lowered for kw in general_keywords):
        return "[TASK:GENERAL_QUERY] " + prompt

    # Summarizer route
    if any(kw in lowered for kw in summarizer_keywords):
        return "[TASK:SUMMARIZER] " + prompt

    return prompt

def extract_path_hint(prompt: str, query_type: QueryType, subtask: SubTaskType) -> str:
    prompt_lower = prompt.lower()
    username = getpass.getuser()
    
    documents_path = f"C:\\Users\\km866\\OneDrive\\Documents\\Documents"
    downloads_path = f"C:\\Users\\km866\\Downloads"

    # Rule 1: If "downloads" or "documents" is mentioned
    if "downloads" in prompt_lower:
        return downloads_path
    if "documents" in prompt_lower:
        return documents_path

    # Rule 2: Based on query type
    if query_type == QueryType.FILE_HANDLING:
        return documents_path

    if query_type in [QueryType.GITHUB_ACTIONS, QueryType.PROJECT_SETUP]:
        drive = "D:\\" if "d drive" in prompt_lower else "C:\\"
        if "new" in prompt_lower or "create" in prompt_lower:
            folder_name = "new_folder"
            # Try to extract folder/project name from the prompt
            tokens = prompt_lower.split()
            for i, word in enumerate(tokens):
                if word in {"folder", "project"} and i + 1 < len(tokens):
                    folder_name = tokens[i + 1].capitalize()
                    break
            return f"{drive}{folder_name}"
        return drive

    return "C:\\"  


def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a smart query processor. Translate natural language queries into structured fields: type, subtask, target, and path.\n"
            "- Default to C:\\Users\\km866\\OneDrive\\Documents\\Documents\\ for FILE_HANDLING.\n"
            "- Downloads path is mentioned C:\\Users\\km866\\Downloads"
            "- Use D:\\ (fallback C:\\) for GITHUB_ACTIONS/PROJECT_SETUP.\n"
            "- Use 'new_folder' or extracted name if creating something new.\n"
            "- Use proper Windows-style absolute paths with capital drive letters.\n"
            "- Extract and preserve file extensions (.pdf, .txt, etc.).\n"
            "- Be accurate with subtask classification.\n"
        ),
        markdown=True,
        response_model=QueryProcessor,
    )

    
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
    query_obj = response.content
    path_hint = extract_path_hint(prompt, query_obj.type, query_obj.subtask)
    query_obj.path = path_hint
    return query_obj
    # return response.content

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
