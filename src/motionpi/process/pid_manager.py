from pathlib import Path

from .storage import Storage

storage = Storage()

PID_FILE = storage.meta_dir / "motion_sensor_process.pid"


def write_pid(pid):
    storage.meta_dir.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(pid))


def read_pid():
    if not PID_FILE.exists():
        return None
    with open(PID_FILE, "r") as f:
        return int(f.read().strip())


def delete_pid():
    if PID_FILE.exists():
        PID_FILE.unlink()


def has_pid():
    return PID_FILE.exists()
