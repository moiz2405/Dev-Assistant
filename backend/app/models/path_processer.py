from agno.agent import Agent, RunResponse
from agno.models.groq import Groq

class Process_Path(BaseModel):
    type : str = Field(..., description = ("correctly extract the path from the users query separating directories with double slashes like \\"))


path_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    response_model = Process_Path
)

while(1):
    prompt = input()
    path_agent.print_response(prompt)