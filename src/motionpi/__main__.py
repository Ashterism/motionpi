from .process.storage import Storage
from .process.pid_manager import has_pid, delete_pid

# Entry point for lapsepi when run with: python -m lapsepi
#
# Responsibilities:
# - Clean up any stale state from previous (possibly dirty) shutdown
# - Start the Flask web server
#
# Future:
# - Hook in graceful shutdown (button / signal handling)

storage = Storage()



def check_last_shutdown():
    lockfile_status = None
    pidfile_status = None

    if storage.check_lockfile("camera_in_use"):
        storage.delete_lockfile("camera_in_use")
        lockfile_status = "deleted"

    if has_pid():
        delete_pid()
        pidfile_status = "deleted"

    dirty_shutdown = "deleted" in (lockfile_status, pidfile_status)

    bootlog = {
        "dirty_shutdown" : dirty_shutdown,
        "lockfile_status" : lockfile_status,
        "pidfile_status" : pidfile_status,
    }

    filepath = storage.meta_dir / "bootlog.json"

    storage.write_json(filepath, bootlog)


def start_flask():
    from lapsepi.web.app import app
    app.run(host="0.0.0.0", port=5002)


def shutdown_gracefully():
    ...


def main():

    check_last_shutdown()
    start_flask()


if __name__ == "__main__":
    main()
