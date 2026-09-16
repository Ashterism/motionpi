import sys
import subprocess
import threading
import time


from ..process import pid_manager as pid
from ..capture.camera import Camera
from ..capture.timelapse import stop_timelapse
from ..capture.motion_trigger import stop_motion_sensor
from ..process.storage import Storage
from ..process.settings_manager import SettingsManager
from ..process.pir_diagnostics import PIRDiagnostics
from ..process.video_maker import create_timelapse_video
from ..hardware.pir import PIR
from ..utils.environment_detector import detect_runmode


# runmode = detect_runmode()
camera = Camera()
storage = Storage()
settings_manager = SettingsManager(storage)
pir_diagnostics = PIRDiagnostics(storage)
_diagnostics_pir = None
_pir_test_thread = None
_pir_test_lock = threading.Lock()

# CONTROL POINTS


def get_photo():
    directory = use_camera("single_image")
    if directory == None:
        return
    camera.take_image(directory)
    camera.close_camera()
    storage.delete_lockfile("camera_in_use")


def get_timelapse(interval, runtime):
    if not interval or not runtime:
        return

    directory = use_camera("timelapse")
    if directory == None:
        return

    timelapse_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "motionpi.capture.timelapse",
            str(directory),
            str(interval),
            str(runtime),
        ]
    )

    pid.write_pid("timelapse", timelapse_process.pid)


def get_sensor_state():
    filepath = storage.meta_dir / "sensor_state.json"
    read_state = storage.read_json(filepath)
    if read_state == None:
        return "off"
    else:
        return read_state


def set_sensor_state(state):
    filepath = storage.meta_dir / "sensor_state.json"

    inactivity_timeout = None # for wiring up later

    if state == "on":
        if storage.check_lockfile("pir_test"):
            return False

        directory = use_camera("timelapse")
        if directory == None:
            return False

        motion_sensor_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "motionpi.capture.motion_trigger",
                str(inactivity_timeout),
            ]
        )

        pid.write_pid("motion_sensor", motion_sensor_process.pid)
        storage.write_json(filepath, state)
        return True

    elif state == "off":
        stop_motion_sensor()
        storage.write_json(filepath, state)
        pir_diagnostics.set_capture_state("idle")
        return True

    return False


def get_timelapse_stopped():
    stop_timelapse()


def get_timelapse_video(session_path, fps):
    return create_timelapse_video(session_path, fps)


def get_settings_options():
    return settings_manager.get_options()


def get_settings():
    return settings_manager.get_settings()


def update_settings(data):
    return settings_manager.update_settings(data)


def get_pir_diagnostics():
    global _diagnostics_pir

    if get_sensor_state() != "on" and not storage.check_lockfile("pir_test"):
        if _diagnostics_pir is None:
            _diagnostics_pir = PIR(detect_runmode())
        pir_diagnostics.record_reading(_diagnostics_pir.motion_detected())

    return pir_diagnostics.snapshot()


def start_pir_test(duration_seconds=60):
    global _pir_test_thread

    with _pir_test_lock:
        if _pir_test_thread and _pir_test_thread.is_alive():
            return False

        storage.create_lockfile("pir_test")
        pir_diagnostics.start_test(duration_seconds)
        _pir_test_thread = threading.Thread(
            target=_run_pir_test,
            args=(duration_seconds,),
            daemon=True,
            name="pir-diagnostics-test",
        )
        _pir_test_thread.start()
        return True


def _run_pir_test(duration_seconds):
    was_motion_on = get_sensor_state() == "on"

    try:
        if was_motion_on:
            set_sensor_state("off")

        test_pir = PIR(detect_runmode())
        deadline = time.monotonic() + duration_seconds

        while time.monotonic() < deadline:
            pir_diagnostics.record_reading(
                test_pir.motion_detected(),
                source="test",
            )
            time.sleep(0.2)

        pir_diagnostics.complete_test()
    except Exception as exc:
        pir_diagnostics.fail_test(exc)
    finally:
        storage.delete_lockfile("pir_test")
        if was_motion_on:
            set_sensor_state("on")


# HELPER


def use_camera(session_type="single_image"):

    # CHECK AND SET LOCKFILE
    if storage.check_lockfile("camera_in_use"):
        return

    storage.create_lockfile("camera_in_use")

    # get the folder to save into
    # then the filenames the camera gets from storage
    directory = storage.build_folder_path(session_type)

    return directory



if __name__ == "__main__":
    # get_photo()
    get_timelapse(5, 15)
    print(pid.read_pid("timelapse"))
