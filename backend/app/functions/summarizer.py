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

def summarizer(pdf_path):
    # Convert Windows-style path to WSL-compatible path if needed
    if is_wsl() and "\\" in pdf_path:
        pdf_path = convert_windows_to_wsl_path(pdf_path)

    pdf_text = extract_text_from_pdf(pdf_path)
    
    agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        knowledge=None,  
    )
    
    print("SUMMARIZER")
    while True:
        question = input("")
        if question.lower() in ['exit', 'quit']:
            print("Exiting")
            break
        full_prompt = f"""Here is a document content:\n\n{pdf_text}\n\nNow, {question}"""
        agent.print_response(full_prompt)
