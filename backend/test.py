import os; print("USERNAME:", os.getenv("GITHUB_USERNAME"))


from app.functions.github_handler import push_folder_to_github

push_folder_to_github("test_repo", "C:\\Users\\Shikhar\\Downloads\\test")

