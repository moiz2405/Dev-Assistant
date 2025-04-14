import os
import subprocess
import requests
from dotenv import load_dotenv

# Load .env from the root of the project

load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), '../../..', '.env.local'))
# if not load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env.local')):
#     print("❌ Failed to load .env.local")




# Fetch credentials
GITHUB_API = "https://api.github.com"
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")

def push_folder_to_github(repo_name, folder_path):
    """
    Creates a GitHub repo and pushes the local folder to it.
    """
    if not USERNAME or not TOKEN:
        raise Exception("❌ GitHub credentials not set in .env file.")

    # Check if repo exists
    check_url = f"{GITHUB_API}/repos/{USERNAME}/{repo_name}"
    check = requests.get(check_url, auth=(USERNAME, TOKEN))
    if check.status_code == 200:
        print(f"📦 Repo '{repo_name}' already exists on GitHub.")
        return

    # Create repo
    print("🚀 Creating GitHub repository...")
    payload = {"name": repo_name, "private": False}
    r = requests.post(f"{GITHUB_API}/user/repos", json=payload, auth=(USERNAME, TOKEN))
    if r.status_code != 201:
        raise Exception(f"❌ Failed to create repo: {r.status_code}, {r.json()}")

    # Initialize Git and push
    print("📁 Initializing local repo and pushing to GitHub...")
    cmds = [
        f'cd "{folder_path}"',
        "git init",
        "git add .",
        'git commit -m "Initial commit"',
        f'git remote add origin https://github.com/{USERNAME}/{repo_name}.git',
        "git branch -M main",
        "git push -u origin main"
    ]
    subprocess.call(" && ".join(cmds), shell=True)
    print(f"✅ Successfully pushed '{repo_name}' to GitHub.")

def list_github_repos():
    """
    Lists all repositories under the authenticated GitHub user.
    """
    if not USERNAME or not TOKEN:
        raise Exception("❌ GitHub credentials not set in .env file.")

    print("📚 Fetching repository list...")
    response = requests.get(f"{GITHUB_API}/user/repos", auth=(USERNAME, TOKEN))

    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            print(f"- {repo['name']} → {repo['html_url']}")
    else:
        print(f"❌ Failed to fetch repositories: {response.status_code}")

    print("✅ Successfully fetched repository list.")

def clone_github_repo(repo_url, target_directory):
    """
    Clones a GitHub repository to the specified target directory.
    """
    if not USERNAME or not TOKEN:
        raise Exception("❌ GitHub credentials not set in .env file.")

    print(f"📥 Cloning {repo_url} into {target_directory}...")
    result = subprocess.run(["git", "clone", repo_url], cwd=target_directory, shell=True)
    if result.returncode == 0:
        print("✅ Successfully cloned GitHub repository.")
    else:
        print("❌ Cloning failed.")

    print("✅ Successfully cloned GitHub repository.")