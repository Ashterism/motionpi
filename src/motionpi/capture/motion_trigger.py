from datetime import datetime
import time
import sys
import logging

from ..utils import logging_config
from ..utils.environment_detector import detect_runmode
from ..process.storage import Storage
from ..process.settings_manager import SettingsManager
from ..process import pid_manager as pid
from ..capture.camera import Camera
from ..hardware.pir import PIR

logger = logging.getLogger(__name__)

# controls process of triggering action and then... when / how to trigger again 

""" CONFIG"""
secs_between_pir_polls = 0.3

storage = Storage()
settings_manager = SettingsManager(storage)
runmode = detect_runmode()
cam = Camera(runmode)
pir = PIR(runmode)

def motion_trigger(inactivity_timeout=None):
    settings = settings_manager.get_settings()
    timeout = (
        inactivity_timeout
        if inactivity_timeout is not None
        else settings["session_timeout_secs"]
    )
    directory = None

    active_session = False
    last_motion_time = None

    while True:
        if pir.motion_detected():
            logger.debug("motion detected")

            if not active_session:
                directory = storage.build_folder_path("timelapse")
                active_session = True
                last_motion_time = datetime.now()
                logger.info(f"Starting motion session: {directory}")

            for _ in range(settings["photo_burst_count"]):
                cam.take_image(directory)
                time.sleep(settings["photo_burst_gap_secs"])

            last_motion_time = datetime.now()
            time.sleep(settings["photo_cooldown_secs"])

        else:
            logger.debug("no motion detected")

            if active_session and last_motion_time:
                idle_time = (datetime.now() - last_motion_time).total_seconds()

                if idle_time > timeout:
                    logger.info("Ending motion session due to inactivity")
                    active_session = False
                    last_motion_time = None
                    directory = None

        time.sleep(secs_between_pir_polls)


def stop_motion_sensor():
    was_killed = pid.kill_pid("motion_sensor")
    if not was_killed:
        return

    storage.delete_lockfile("camera_in_use")



if __name__ == "__main__":
    inactivity_timeout = None
    if len(sys.argv) > 1 and sys.argv[1] != "None":
        inactivity_timeout = int(sys.argv[1])

    motion_trigger(inactivity_timeout)
