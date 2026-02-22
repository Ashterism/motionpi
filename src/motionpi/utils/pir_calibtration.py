import time
from datetime import datetime

from ..pir import PIR
from .environment_detector import detect_runmode

    
def pir_calibration():
    
    runmode = detect_runmode()
    pir = PIR(runmode)

    last_reading = None
    last_reading_time = datetime.now()

    #loop until ctrl+c
    print("Looping until exited with ctrl+c")
    while True:
        pir_reading = pir.motion_detected()
        pir_reading_time = datetime.now()
        if pir_reading == last_reading:
            time_in_state = (pir_reading_time - last_reading_time).total_seconds
        else:
            time_in_state = 0
            last_reading_time = pir_reading_time

        # show reading
        print(f"State   {pir_reading}   for {time_in_state} secs")

        last_reading = pir_reading
   
        time.sleep(1)

