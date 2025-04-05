from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from typing import Iterator 
from pydantic import BaseModel, Field
from rich.pretty import pprint  

class query_processor(BaseModel):
    type : str = Field(..., description = "Type of query FROM GENERAL,FILE_HANDLING, PROJECT_SETUP,SUMMARIZER, APP")
    command : str = Field(..., description = "provide the task command from : OPEN,CLOSE,DELETE,OTHER,")
    target : str = Field(..., description = "extract the target maybe an app, file, repo name etc ex, whatsapp, myfile.txt, etc, will mostly be ")
    path : str = Field(..., description = "Give correct windows path only single '\'OUTPUT IN ABSOLUTE PATH , Extract path from the query, default documents for file_handling , c drive for project_setup and downloads for other, ")

class query(BaseModel):
    type : str = Field(..., description="Correctly determine the type of Query from 1) file_handling(if query is about searching , opening or closing a file ), 2) app_handling (if query asked for opening or closing an app), 3) project_setup(if query asks to setup an new project or a existing project from github or somewhere) 4) summarizer(if query asks to summarize a pdf/document or wants to ask questions from a pdf/documents) 5) general_query(if user didnt gave a task but asked a question about something)")
    subtype : str = Field(..., description="This is the subtype of the type determined above , correctly determine this for types subtypes are 1) file_handling(search_file, open_file, close_file), 2) app_handling(open_app,close_app), 3) project_setup(new_project, existing_project) 4)summarizer(summarize, answer_query")
    target : str = Field(..., description="Determine the target of the query target for above types can be 1)file_handling(file name with extension ex - college.pdf, accounts.txt etc ) 2) app_handling(valid app name ex - whatsapp, ark browser, chrome , vs code, terminal , file explorer) 3) project_setup(project_type if new project to setyp, project_name if existing project to setup) ,4)summarizer(file name again , ex project.pdf etc) ")
    path : str = Field(..., description="determine the correct path for the file mentioned about, follow windows path with (single) \ between directories 1) if path is given like (C:\my_file) if defined, 2) if user asks to make a new folder or setup a new project then extract the folder name if given by user else give (C:\new folder) or (D:\new folder) which ever matched with the query ,  by default give Documents for files ")

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