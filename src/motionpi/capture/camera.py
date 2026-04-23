import time
from ..process.storage import Storage
from ..process.last_image import update_last_image_taken

from ..mocks.mock_file_maker import create_mock_jpg
from ....archive.utils.environment_detector import detect_runmode


storage = Storage()


""" later on... move cam start from init to take image to save battery """


# handles image/video capture; delegates file paths to Storage; switches between real and mock based on mode
class Camera:

    def __init__(self, mode=None):
        self.mode = mode or detect_runmode()
        self.cam = None
        self.initialised = False

    def _init_camera(self):
        if self.mode == "prod" and not self.initialised:
            from picamera2 import Picamera2

            self.cam = Picamera2()

            still_config = self.cam.create_still_configuration()
            self.cam.configure(still_config)
            self.cam.start()

            self.initialised = True

    # capture a single image; uses real camera in prod, mock file in dev
    def take_image(self, directory):
        if self.mode == "prod":
            if not self.initialised:
                self._init_camera()
            filepath = storage.build_image_filepath(directory)
            self.cam.capture_file(filepath)

        elif self.mode == "dev":
            time.sleep(0.1)
            filepath = storage.build_image_filepath(directory)
            create_mock_jpg(filepath)

        update_last_image_taken(filepath)


    def close_camera(self):
        if self.mode == "prod" and self.cam:
            try:
                self.cam.stop()
                self.cam.close()
            except Exception:
                pass  # don’t let cleanup crash things

            self.cam = None
            self.initialised = False