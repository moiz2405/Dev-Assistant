# import os; print("USERNAME:", os.getenv("GITHUB_USERNAME"))


# from app.functions.github_handler import push_folder_to_github, list_github_repos, search_repo_url

# # push_folder_to_github("test_repo", "/mnt/c/Users/km866/Downloads/test_folder")
# # list_github_repos()

# repo_url = search_repo_url("acc")
# print(repo_url)

from app.models.groq_preprocess import cached_process_query
# from app.models.test_preprocess import cached_process_query
from app.query_processor import determine_function
while(1):
    prompt = input()
    determine_function(cached_process_query(prompt))