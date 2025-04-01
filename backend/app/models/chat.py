from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from typing import Iterator 
from pydantic import BaseModel, Field
from rich.pretty import pprint  


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True,
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