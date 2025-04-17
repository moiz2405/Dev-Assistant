# pdfs for other files summarizer
# likely use the pdf as context and answer questions  
import os
import platform
from agno.models.groq import Groq
from PyPDF2 import PdfReader
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.utils.pprint import pprint_run_response

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def convert_windows_to_wsl_path(win_path):
    if win_path.startswith("C:\\"):
        return win_path.replace("C:\\", "/mnt/c/").replace("\\", "/")
    return win_path

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def get_agent() -> Agent:
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description=(
            "You are a PDF Summarizer, which explains user queries from a given document"
            "Determine if the user query is a brief / descriptive / small one and answer aptly"
        ),
        markdown=True,
        # response_model=QueryProcessor,
    )

AGENT_MAIN = get_agent()
AGENT_GENERAL = Agent(model=Groq(id="llama-3.3-70b-versatile"))

def summarizer(pdf_path):
    # Convert Windows-style path to WSL-compatible path if needed
    if is_wsl() and "\\" in pdf_path:
        pdf_path = convert_windows_to_wsl_path(pdf_path)

    pdf_text = extract_text_from_pdf(pdf_path)
    
    print("SUMMARIZER")
    while True:
        question = input("")
        if question.lower() in ['exit', 'quit']:
            print("Exiting")
            break
        full_prompt = f"""Here is a document content:\n\n{pdf_text}\n\nNow, {question}"""
        response = AGENT_MAIN.run(full_prompt, stream=False)
        response: RunResponse = AGENT_MAIN.run(full_prompt)
        # output = response.content
        pprint_run_response(response, markdown=True)
        # print(output)
        