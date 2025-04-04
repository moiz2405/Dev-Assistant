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

class SuggestProjectIdea(BaseModel):
    idea_name:str = Field(...,description = "give a unique and solid project idea name")
    idea_requirement:str = Field(...,description = "give 3 purposes of suggesting this project idea")
    business_model:str = Field(...,description = "explain how this can be made into a business model in 5 lines minimum")

# file handling 
class query_processor(BaseModel):
    command:str = Field(...,description = "answer in OPEN or CLOSE or SEARCH based on user input , read user intention carefully")
    file_name :str= Field(..., description = "extract the name of the file with the extension used")
    path :str = Field(..., description= "extract the path from the user query")


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description = "you provide a project idea on the domain given by user",
    markdown=True,
    response_model=query_processor,
    # response_model = ProjectIdea,
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