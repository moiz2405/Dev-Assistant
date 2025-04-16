from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from pydantic import BaseModel, Field

class Process_Path(BaseModel):
    type: str = Field(
        ...,
        description=(
            "Extract a valid file or folder path from the user's input. "
            "Return it using single backslashes (\\) for all paths.\n"
            "Paths may start with:\n"
            "- C:\\\n"
            "- D:\\\n"
            "- Documents\\\n"
            "- Downloads\\\n"
            "Append all relevant subdirectories or filenames.\n"
            "Return only the final path, with correct formatting."
        )
    )

path_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    response_model=Process_Path
)

while True:
    prompt = input("Enter a path-related request:\n")
    path_agent.print_response(
        f"""Extract a properly formatted file or folder path from this request:

"{prompt}"

Instructions:
- Use only single backslashes (\\) throughout the path.
- Start the path with one of:
  - C:\
  - D:\
  - Documents\
  - Downloads\
- Append the subfolders and files from the request.
- Return just the final path string (no explanations or quotes)."""
    )
