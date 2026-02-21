from datetime import datetime
import time
import logging

from .utils import logging_config
from .utils.environment_detector import detect_runmode
from .storage import Storage
from .camera import Camera
from .pir import PIR

logger = logging.getLogger(__name__)


""" contorls process of triggering action and then... when / how to trigger again 
    run this file only, use: PYTHONPATH=src python -m motionpi.motion_trigger """

def motion_trigger():

    runmode = detect_runmode()
    cam = Camera(runmode)
    pir = PIR(runmode)
    storage = Storage()


    """ MOVE TO CONFIG """

    secs_between_pir_polls = 0.3

    photo_burst_count = 3
    photo_burst_gap_secs = 0.5
    photo_cooldown_in_secs = 8

    """ just the above """

#video_length_in_secs = 10

    keep_running = True

    storage.ensure_runtime_dirs()

    last_trigger_time = datetime.now()

    while keep_running:
        if pir.motion_detected() == 1:
            timepassed = (datetime.now() - last_trigger_time).total_seconds()
            logger.debug(f"time passed: {timepassed}")

            for shots in range(photo_burst_count):
                cam.take_image()
                time.sleep(photo_burst_gap_secs)
                
            last_trigger_time = datetime.now()
            time.sleep(photo_cooldown_in_secs)

        else:
            logger.debug("no motion detected")
            pass
        time.sleep(secs_between_pir_polls)




if __name__ == "__main__":
    motion_trigger()
