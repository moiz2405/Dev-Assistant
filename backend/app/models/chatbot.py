from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from typing import Iterator 
from pydantic import BaseModel, Field
from rich.pretty import pprint  

class ProjectIdea(BaseModel):
    requirement: str = Field(...,description = "Explain why the given project idea is required")
    usecases: str = Field(...,description = "Give 3 one word usecases of the project idea")
    views: str = Field(..., description = "Provide your views on the idea and any improvements")

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description = "you evaluate project ideas given to you",
    markdown=True,
    response_model = ProjectIdea,
)

while(1):
    prompt = input()
    agent.print_response(prompt,stream = True)


# pure stream output 
# while(1):
#     prompt = input()
#     output : Iterator[RunResponse] = agent.run(prompt,stream = True)
#     for curr in output:
#         print(curr.content)    