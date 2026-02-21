"""
Docstring for motionpi.pir

"GPIO.input(PIR_PIN)" will return either:
1 (high) or 0 (low)
1 is equivalent to true in python if logic

"""

import time
import csv
from pathlib import Path


class PIR:

    def __init__(self, mode="dev"):

        self.mode = mode

        if self.mode == "prod":
            # setup for REAL PIR input
            import RPi.GPIO as GPIO

            self.GPIO = GPIO

            # on pi run:
            # python3 -c "from picamera2 import Picamera2; print('ok')"

            self.GPIO.setmode(self.GPIO.BCM)
            self.PIR_PIN = 17
            self.GPIO.setup(self.PIR_PIN, self.GPIO.IN)

        else:
            # load mock data once
            rootpath = Path(__file__).resolve().parent
            mock_path = rootpath / "mocks" / "mock_pir.csv"

            with open(mock_path, "r") as f:
                reader = csv.reader(f)
                self.mock_rows = [int(row[0]) for row in reader]

            self.mock_index = 0

    def motion_detected(self):
        if self.mode == "prod":
            return self.GPIO.input(self.PIR_PIN)
        else:
            value = self.mock_rows[self.mock_index]

            self.mock_index += 1
            if self.mock_index >= len(self.mock_rows):
                self.mock_index = 0  # loop

            return int(value)
