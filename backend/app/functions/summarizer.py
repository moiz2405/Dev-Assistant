# pdfs for other files summarizer
# likely use the pdf as context and answer questions  
import os
import platform
from agno.agent import Agent
from agno.models.groq import Groq
from PyPDF2 import PdfReader

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
            "You are a smart query processor. Translate natural language queries into structured fields: type, subtask, target, and path.\n"
            "- Default to C:\\Users\\km866\\OneDrive\\Documents\\Documents\\ for FILE_HANDLING.\n"
            "- Downloads path is mentioned C:\\Users\\km866\\Downloads"
            "- Use D:\\ (fallback C:\\) for GITHUB_ACTIONS/PROJECT_SETUP.\n"
            "- Use 'new_folder' or extracted name if creating something new.\n"
            "- Use proper Windows-style absolute paths with capital drive letters.\n"
            "- Extract and preserve file extensions (.pdf, .txt, etc.).\n"
            "- Be accurate with subtask classification.\n"
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
        agent.print_response(full_prompt)
