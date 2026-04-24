import os
import signal

from .storage import Storage

storage = Storage()

def get_pid_file(process_name):
    return storage.meta_dir / f"{process_name}.pid"


def write_pid(process_name, pid):
    pid_file = get_pid_file(process_name)
    storage.meta_dir.mkdir(parents=True, exist_ok=True)
    with open(pid_file, "w") as f:
        f.write(str(pid))


def read_pid(process_name):
    pid_file = get_pid_file(process_name)
    if not pid_file.exists():
        return None
    with open(pid_file, "r") as f:
        return int(f.read().strip())


def delete_pid(process_name):
    pid_file = get_pid_file(process_name)
    if pid_file.exists():
        pid_file.unlink()


def has_pid(process_name):
    pid_file = get_pid_file(process_name)
    return pid_file.exists()

def kill_pid(process_name):
    process_id = read_pid(process_name)
    if process_id is None:
        return False

    try:
        os.kill(process_id, signal.SIGTERM)
    except ProcessLookupError:
        delete_pid(process_name)
        return False

    delete_pid(process_name)
    return True
