import os; print("USERNAME:", os.getenv("GITHUB_USERNAME"))


from app.functions.github_handler import push_folder_to_github

push_folder_to_github("test_repo", "/mnt/c/Users/km866/Downloads/test_folder")

