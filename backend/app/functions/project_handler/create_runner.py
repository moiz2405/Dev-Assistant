# create_runner.py
import time
from app.functions.project_handler.create_project import setup_project, check_project_status
from app.functions.logger import logger

def run_project_setup(target, parent_path="D://va_projects"):
    active_processes = {}

    process_id = setup_project(target, parent_path)
    if not process_id:
        return

    active_processes[process_id] = {
        "type": target,
        "path": parent_path,
        "status": "RUNNING"
    }

    print(f"Started process {process_id} for {target} project")
    logger.info(f"Started process {process_id} for {target} project")

    try:
        while active_processes:
            pid, msg = check_project_status()
            if pid:
                print(f"[{pid}] {msg}")
                if msg in ["COMPLETED", "FAILED"]:
                    active_processes[pid]["status"] = msg

            completed = [p for p, info in active_processes.items()
                         if info["status"] in ["COMPLETED", "FAILED"]]
            for p in completed:
                del active_processes[p]

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting... (background processes will continue)")
