import queue

log_queue = queue.Queue()

def log(msg):
    print(msg)
    log_queue.put(msg)

def info(msg):
    log(f"[INFO] {msg}")

def success(msg):
    log(f"[DONE] {msg}")

def error(msg):
    log(f"[ERROR] {msg}")

def section(msg):
    log(f"\n--- {msg} ---")
