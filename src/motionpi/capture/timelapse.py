import time, sys, os
from pathlib import Path

from .camera import Camera
from ..process.storage import Storage
from ..process.last_image import read_last_image_taken
from ...src.motionpi.process import pid_manager as pid

camera = Camera()
storage = Storage()


def run_timelapse(directory, interval=5, runtime=15):

    directory = Path(directory)

    photos_to_take = int(runtime / interval)

    for i in range(photos_to_take):
        camera.take_image(directory)
        if i < photos_to_take - 1:
            time.sleep(interval)

    camera.close_camera()
    storage.delete_lockfile("camera_in_use")
    pid.delete_pid()


def stop_timelapse():
    timelapse_pid = pid.read_pid()
    if not timelapse_pid:
        return
    try:
        os.kill(timelapse_pid, 15)
    except ProcessLookupError:
        pass  # process already dead

    # kill process
    # write json to folder
    # name  terminated.json
    # with  datetime: time killed
    # and   reason: manual_termination

    file_path = read_last_image_taken()
    session_dir = storage.data_dir / Path(file_path).parent
    termination_log = session_dir / "terminated.json"

    datestamp = storage.create_datestamp() + "_" + storage.create_timestamp()

    content = {
        "datetime": datestamp,
        "reason": "manual_termination",
    }

    camera.close_camera
    storage.write_json(termination_log, content)
    storage.delete_lockfile("camera_in_use")
    pid.delete_pid()



if __name__ == "__main__":
    # remember this is run as a subprocess, so need to convert sys.argvs
    directory = sys.argv[1]
    interval = int(sys.argv[2])
    runtime = int(sys.argv[3])

    run_timelapse(directory, interval, runtime)