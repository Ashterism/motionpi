import time
from .storage import Storage

storage = Storage()


""" later on... move cam start from init to take image to save battery """


class Camera:

    def __init__(self, mode="dev"):
        self.mode = mode
        if self.mode == "prod":
            # setup for REAL camera
            from picamera2 import Picamera2
            self.cam = Picamera2()

            # Configure once for still capture and start camera
            still_config = self.cam.create_still_configuration()
            self.cam.configure(still_config)
            self.cam.start()

        else:
            # set up mock
            ...


    def take_image(self):
        if self.mode == "prod":
            filepath = storage.build_media_path("image")
            self.cam.capture_file(filepath)

        elif self.mode == "dev":
            time.sleep(0.1)
            storage.create_mock_file("image")


    def take_video(self, duration=10):
        if self.mode == "prod":
            from picamera2.encoders import H264Encoder
            from picamera2.outputs import FfmpegOutput

            filepath = storage.build_media_path("video")

            # Configure the camera for video capture before recording
            video_config = self.cam.create_video_configuration(main={"size": (1920, 1080)})
            self.cam.configure(video_config)
            self.cam.start()

            encoder = H264Encoder(bitrate=8_000_000)
            output = FfmpegOutput(filepath)

            self.cam.start_recording(encoder, output)
            time.sleep(duration)
            self.cam.stop_recording()
            self.cam.stop()

        elif self.mode == "dev":
            storage.create_mock_file("video")
