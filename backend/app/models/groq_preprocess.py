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
    path: str = Field(
        ...,
        description=(
           "Determine the correct full Windows-style path for the file or folder referenced in the query."
            "Guidelines:"
            "For documents and downlaods in path return them directly as Documents\\ and Downloads\\ without any parent c or d drive they standalone "
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

    # Rule 1: If "downloads" or "documents" is mentioned
    if "downloads" in prompt_lower:
        return "Downloads\\"
    if "documents" in prompt_lower:
        return "Documents\\"

    # Rule 2: Based on query type
    if query_type == QueryType.FILE_HANDLING:
        return "Documents\\"

    if query_type in [QueryType.GITHUB_ACTIONS, QueryType.PROJECT_SETUP]:
        drive = "D:\\" if "d drive" in prompt_lower else "C:\\"
        if "new" in prompt_lower or "create" in prompt_lower:
            folder_name = "new_folder"
            # Try to extract folder name from the prompt
            tokens = prompt_lower.split()
            for i, word in enumerate(tokens):
                if word in {"folder", "project"} and i + 1 < len(tokens):
                    folder_name = tokens[i + 1].capitalize()
                    break
            return f"{drive}{folder_name}"
        return drive

    return "C:\\"  # fallback

def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a smart query processor. Your job is to translate natural language user queries "
            "into structured data with fields: type, subtask, target, and path.\n"
             "You are a smart query processor. Translate natural language queries into structured fields: type, subtask, target, and path.\n"
            "- Use Documents\\ or Downloads\\ if mentioned, no full path or user folder required.\n"
            "- Use Documents\\ as default for FILE_HANDLING queries.\n"
            "- Use D:\\ (or fallback to C:\\) for GITHUB_ACTIONS and PROJECT_SETUP unless user mentions otherwise.\n"
            "- If 'create' or 'new' is mentioned, return drive + new_folder or drive + project/folder name if found.\n"
            "- Paths should follow Windows format using single backslashes and capital drive letters.\n"
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
