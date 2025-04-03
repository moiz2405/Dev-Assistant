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

class query_processor(BaseModel):
    type : str = Field(..., description = "Type of query FROM GENERAL,FILE_HANDLING, PROJECT_SETUP,SUMMARIZER, APP")
    command : str = Field(..., description = "provide the task command from : OPEN,CLOSE,DELETE,OTHER,")
    target : str = Field(..., description = "extract the target maybe an app, file, repo name etc ex, whatsapp, myfile.txt, etc, will mostly be ")
    path : str = Field(..., description = "Give correct windows path only single '\'OUTPUT IN ABSOLUTE PATH , Extract path from the query, default documents for file_handling , c drive for project_setup and downloads for other, ")


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description = "you are an query processor , tranlate natural language to commands",
    markdown=True,
    response_model = query_processor,
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