from enum import Enum
from typing import Iterator
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.groq import Groq

# ───────────────────────────────
# ENUMS FOR VALIDATED VALUES
# ───────────────────────────────

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

# ───────────────────────────────
# STRUCTURED MODELS FOR QUERY PROCESSING
# ───────────────────────────────

class QueryProcessor(BaseModel):
    """
    Translated and structured output from user query.
    """
    type: QueryType = Field(
        ..., 
        description=(
            "Type of query from: GENERAL, FILE_HANDLING (search/open/close a file), "
            "PROJECT_SETUP (new/existing projects), SUMMARIZER (summarizing or answering from documents), APP (open/close apps)"
        )
    )
    command: CommandType = Field(
        ..., 
        description=(
            "Command for the action: OPEN, CLOSE, DELETE, OTHER (like summarizing, querying from file, etc.)"
        )
    )
    target: str = Field(..., description="Target app, file, project, etc.")
    path: str = Field(..., description="Windows absolute path (use single \ like C:\new folder) or (D:\"new folder)) only")


# ───────────────────────────────
# PRE-PROMPT BOOSTER (OPTIONAL)
# ───────────────────────────────

def boost_prompt(prompt: str) -> str:
    summarizer_keywords = [
        "summarize", "answer from", "explain from", "read from", "understand from", 
        "questions from", "query from", "explain this pdf", "tell from"
    ]
    lowered = prompt.lower()
    if any(kw in lowered for kw in summarizer_keywords):
        return "[TASK:SUMMARIZER] " + prompt
    return prompt

# ───────────────────────────────
# AGENT SETUP
# ───────────────────────────────

def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a query processor. Translate user queries into structured commands. "
            "Pay close attention to whether a user is asking to summarize or extract information from a document like a PDF. "
            "Treat these as type='SUMMARIZER' and command='OTHER'."
        ),
        markdown=True,
        response_model=QueryProcessor,
    )

# ───────────────────────────────
# MAIN CLI INTERACTION LOOP
# ───────────────────────────────

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

# ───────────────────────────────
# OPTIONAL: STREAMING OUTPUT
# ───────────────────────────────

def stream_loop():
    agent = get_agent()
    while True:
        prompt = input(">>> ")
        boosted = boost_prompt(prompt)
        output: Iterator[RunResponse] = agent.run(boosted, stream=True)
        for curr in output:
            print(curr.content)

# ───────────────────────────────
# ENTRY POINT
# ───────────────────────────────

if __name__ == "__main__":
    main_loop()
