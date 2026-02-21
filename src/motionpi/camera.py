import time
from .storage import Storage

storage = Storage()


class Camera:

    def __init__(self, mode="dev"):
        self.mode = mode
        if self.mode == "prod":
            # setup for REAL camera
            from picamera2 import Picamera2

            self.cam = Picamera2()

            ...

        else:
            # set up mock
            ...

    def take_image(self):
        if self.mode == "prod":
            filepath = storage.build_media_path("image")
            self.cam.capture(filepath)

        elif self.mode == "dev":
            time.sleep(0.1)
            storage.create_mock_file("image")

    # def take_video(self):
    #     if self.mode == "prod":
    #         filepath = storage.build_media_path("video")
    #         self.cam.start_recording(filepath)

    #     elif self.mode == "dev":
    #         storage.create_mock_file("video")
