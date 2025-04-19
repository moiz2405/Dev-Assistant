import os
import subprocess

def setup_project(project_type: str, path: str):
    """
    Sets up a project based on the type provided.
    
    Parameters:
    - project_type: Type of the project ('react', 'next', 'flask', 'django')
    - path: Directory path to create the project
    """
    
    # Normalize inputs
    project_type = project_type.lower()
    path = os.path.abspath(path)
    
    os.makedirs(path, exist_ok=True)
    os.chdir(path)

    try:
        if project_type == "react":
            subprocess.run(["npx", "create-react-app", "."], check=True)

        elif project_type == "next":
            subprocess.run(["npx", "create-next-app@latest", ".", "--ts"], check=True)

        elif project_type == "flask":
            os.makedirs("app", exist_ok=True)
            with open("app/__init__.py", "w") as f:
                f.write("""from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return "Hello, Flask!"\n""")
            with open("run.py", "w") as f:
                f.write("from app import app\n\nif __name__ == '__main__':\n    app.run(debug=True)\n")
            subprocess.run(["pip", "install", "flask"], check=True)

        elif project_type == "django":
            subprocess.run(["pip", "install", "django"], check=True)
            subprocess.run(["django-admin", "startproject", "config", "."], check=True)

        else:
            raise ValueError("Unsupported project type. Use 'react', 'next', 'flask', or 'django'.")

        print(f"{project_type.capitalize()} project set up successfully at {path}.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
