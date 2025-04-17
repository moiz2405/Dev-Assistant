import os
import platform
import subprocess
import sys
from agno.models.groq import Groq
from PyPDF2 import PdfReader
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
            "You are a PDF Summarizer that explains user queries from a given document. "
            "Determine if the user query is brief/descriptive/small and answer aptly."
        ),
        markdown=True,
    )

AGENT_MAIN = get_agent()

def summarizer(pdf_path):
    if is_wsl() and "\\" in pdf_path:
        pdf_path = convert_windows_to_wsl_path(pdf_path)

    pdf_text = extract_text_from_pdf(pdf_path)

    print("Summarizer")

    while True:
        question = input("")
        if question.lower() in ['exit', 'quit']:
            print("Exiting")
            break
        full_prompt = f"Here is a document content:\n\n{pdf_text}\n\nNow, {question}"
        response: RunResponse = AGENT_MAIN.run(full_prompt)
        pprint_run_response(response, markdown=True)
        
def summarize_in_new_window(pdf_path):
    if is_wsl():
        wsl_script_path = "/mnt/d/projects/MYPROJECTS/Dev-Assistant/backend/app/functions/summarizer.py"
        wsl_pdf_path = convert_windows_to_wsl_path(pdf_path)

        # Combine script + PDF path into one command
        full_command = f"python3 {wsl_script_path} {wsl_pdf_path}"

        # Call a new WSL terminal using Windows Terminal (`wt`) with WSL profile
        subprocess.Popen([
            "powershell.exe", "-Command",
            f"wt wsl -e bash -c \"{full_command}\""
        ])


# If run directly, start summarizer with CLI path
if __name__ == "__main__":
    if len(sys.argv) > 1:
        summarizer(sys.argv[1])
    else:
        print("Please provide a PDF path as an argument.")
