from enum import Enum
from typing import Iterator
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq

class QueryType(str, Enum):
    GENERAL = "GENERAL"
    FILE_HANDLING = "FILE_HANDLING"
    PROJECT_SETUP = "PROJECT_SETUP"
    SUMMARIZER = "SUMMARIZER"
    APP = "APP"

class CommandType(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    DELETE = "DELETE"
    OTHER = "OTHER"

class QueryProcessor(BaseModel):
    """
    Structured output parsed from user query.
    """
    type: QueryType = Field(
        ..., 
        description=(
            "Correctly determine the type of query:"
            "1) FILE_HANDLING — if the query is about searching, opening, or closing a file."
            "2) APP — if the query is about opening or closing an app."
            "3) PROJECT_SETUP — if the query is about creating or setting up a new/existing project."
            "4) SUMMARIZER — if the query asks to summarize or extract answers from a document (PDF, DOCX, etc)."
            "5) GENERAL — if no clear task is mentioned, and it's a general question or informational query."
        )
    )
    command: CommandType = Field(
        ..., 
        description=(
            "Determine the specific command to perform within the type above:"
            "- For FILE_HANDLING: OPEN, CLOSE, DELETE"
            "- For APP: OPEN or CLOSE"
            "- For SUMMARIZER: usually OTHER (like summarize, ask questions from doc)"
            "- For PROJECT_SETUP: OPEN (existing), DELETE (cleanup), or NEW_PROJECT (initialize new)"
            "- Use OTHER if not clearly mapped."
        )
    )
    target: str = Field(
        ..., 
        description=(
            "Extract the exact name of the file, app, or project the query refers to:"
            "- For FILE_HANDLING: file name with extension (e.g., report.pdf, data.txt)"
            "- For APP: valid application names (e.g., Chrome, VS Code, WhatsApp, Terminal)"
            "- For PROJECT_SETUP: name of the project or template"
            "- For SUMMARIZER: document file name (e.g., notes.pdf)"
        )
    )
    path: str = Field(
        ..., 
        description=(
            "Determine the correct Windows path (use single `\\`):"
            "- If the path is mentioned, use it directly (e.g., C:\\Documents\\project)"
            "- If the query involves setting up a new folder, extract folder name or default to `C:\\new folder` or `D:\\new folder`"
            "- If not explicitly mentioned, use a safe default Documents"
        )
    )

def boost_prompt(prompt: str) -> str:
    summarizer_keywords = [
        "summarize", "answer from", "explain from", "read from", "understand from", 
        "questions from", "query from", "explain this pdf", "tell from"
    ]
    lowered = prompt.lower()
    if any(kw in lowered for kw in summarizer_keywords):
        return "[TASK:SUMMARIZER] " + prompt
    return prompt

def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a query processor AI. Your job is to analyze user natural language queries "
            "and convert them into structured commands with proper type, command, target, and path. "
            "Carefully assess whether it's a file action, app control, project setup, or document summarization. "
            "If unclear, default to GENERAL."
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
