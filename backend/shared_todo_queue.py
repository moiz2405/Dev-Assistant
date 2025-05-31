import fcntl
import json
import os

QUEUE_FILE = "queue.json"

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return data

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(queue, f)
        fcntl.flock(f, fcntl.LOCK_UN)

def enqueue(task):
    queue = load_queue()
    queue.append(task)
    save_queue(queue)

def dequeue():
    queue = load_queue()
    if not queue:
        return None
    task = queue.pop(0)
    save_queue(queue)
    return task
