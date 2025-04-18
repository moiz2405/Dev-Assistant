import os
import sys
import platform
import subprocess
import difflib

from agno.models.groq import Groq
from PyPDF2 import PdfReader
from agno.agent import Agent, RunResponse
from agno.utils.pprint import pprint_run_response
indexed_files_cache = {}

def is_wsl():
    return 'microsoft' in platform.uname().release.lower()

def convert_to_wsl_path(win_path: str) -> str:
    if ":" in win_path:
        drive, rest = win_path.split(":", 1)
        drive = drive.lower()
        rest = rest.replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return win_path

def normalize_filename(name):
    """Normalize filename by lowercasing and replacing underscores, hyphens, and spaces with a common separator."""
    return name.lower().replace('_', ' ').replace('-', ' ').strip()

def index_files_in_path(search_path):
    """
    Index all files in a directory (recursively) and cache it.
    :param search_path: Base path to search.
    :return: List of full file paths.
    """
    global indexed_files_cache

    if is_wsl():
        search_path = convert_to_wsl_path(search_path)

    indexed_files = []
    for root, _, files in os.walk(search_path):
        for file in files:
            full_path = os.path.join(root, file)
            indexed_files.append(full_path)

    # Store cache by normalized path
    indexed_files_cache[normalize_filename(search_path)] = indexed_files
    return indexed_files


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

def fuzzy_search_file(stt_filename, search_path):
    """
    Fuzzy search for a file using STT input to tolerate typos or phonetically similar names.
    Silently returns best match without user prompts.

    :param stt_filename: The filename received via voice (can have typos).
    :param search_path: The directory to search in.
    :return: Best match file path or None.
    """
    global indexed_files_cache

    # Convert to WSL path if needed
    if is_wsl():
        search_path = convert_to_wsl_path(search_path)

    normalized_path = normalize_filename(search_path)

    # Index files if not cached
    if normalized_path not in indexed_files_cache:
        print(f"Indexing files in: {search_path}")
        indexed_files_cache[normalized_path] = index_files_in_path(search_path)

    all_files = indexed_files_cache[normalized_path]
    if not all_files:
        return None

    normalized_input = normalize_filename(stt_filename)
    file_name_map = {normalize_filename(os.path.basename(f)): f for f in all_files}
    all_normalized_names = list(file_name_map.keys())

    # Close matches
    close_matches = difflib.get_close_matches(normalized_input, all_normalized_names, n=5, cutoff=0.5)
    # Also include partial contains matches
    partial_matches = [name for name in all_normalized_names if normalized_input in name]

    combined_matches = list(dict.fromkeys(close_matches + partial_matches))  # Unique

    if not combined_matches:
        return None

    # Return best match path
    return file_name_map[combined_matches[0]]

def summarize_in_new_window(folder_path, spoken_filename):
    # Always run fuzzy search
    full_file_path = fuzzy_search_file(spoken_filename, folder_path)
    print(full_file_path)
    if not full_file_path:
        print(f"No match found for '{spoken_filename}' in {folder_path}")
        return

    if is_wsl():
        wsl_project_dir = "/mnt/d/projects/MYPROJECTS/Dev-Assistant"
        wsl_script_path = f"{wsl_project_dir}/backend/app/functions/summarizer.py"
        wsl_pdf_path = convert_windows_to_wsl_path(full_file_path)

        # Load GROQ_API_KEY from .env.local
        env_path = os.path.join(wsl_project_dir, ".env.local")
        groq_api_key = ""
        try:
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith("GROQ_API_KEY="):
                        groq_api_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
        except FileNotFoundError:
            print(f".env.local file not found at {env_path}")
            return

        if not groq_api_key:
            print("GROQ_API_KEY not found in .env.local")
            return

        # Final WSL command
        full_command = (
            f"cd {wsl_project_dir} && "
            f"export GROQ_API_KEY='{groq_api_key}' && "
            f"source venv/bin/activate && "
            f"python3 {wsl_script_path} \"{wsl_pdf_path}\""
        )
        print("Executing command:", full_command)

        subprocess.Popen([
            "powershell.exe", "-Command",
            f"Start-Process wt -ArgumentList 'wsl bash -c \"cd /mnt/d/projects/MYPROJECTS/Dev-Assistant && export GROQ_API_KEY=\"{groq_api_key}\" && source venv/bin/activate && python3 /mnt/d/projects/MYPROJECTS/Dev-Assistant/backend/app/functions/summarizer.py \"{wsl_pdf_path}\"\"'"
            ])
        # subprocess.Popen([
        #     "powershell.exe", "-Command",
        #     f"wt wsl -e bash -c \"{full_command}\""
        # ])
        
    else:
        # Native Windows version (optional, add your logic if needed)
        print("Native Windows launch is not fully implemented yet.")

def run_summarizer(pdf_path=None):
    if pdf_path is None and len(sys.argv) <= 1:
        print("Please provide a PDF path as an argument.")
        return
    
    if pdf_path is None:
        pdf_path = sys.argv[1]
    
    summarizer(pdf_path)


# If run directly, start summarizer with CLI path
if __name__ == "__main__":
    run_summarizer()
