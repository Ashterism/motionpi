from datetime import datetime
from pathlib import Path

"""
    
  timestamp_utc = datetime.now(timezone.utc)
    timestamp_local = datetime.now().strftime("%D/%M/%y %H:%M:%S")
    
    data_dir.mkdir(parents=True, exist_ok=True)
    dailies_dir.mkdir(parents=True, exist_ok=True)
"""


class Storage:
    def __init__(self):
        # save directories into temp memory)
        base_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = base_dir / "data"  # /motionpi/data/
        self.images_dir = data_dir / "images"  # /motionpi/data/images/
        self.videos_dir = data_dir / "videos"  # /motionpi/data/videos/

    # HELPERS
    def ensure_runtime_dirs(self):
        # and if not existingv... create them
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    def create_timestamp(self):
        return(datetime.now().strftime("%H-%M-%S"))

    def create_datestamp(self):
        return(datetime.now().strftime("%Y-%m-%d"))


    # DOERS
    def build_media_path(self, file_type):
        if file_type == "image":
            base_directory = self.images_dir
            prefix = "img_"
            extension = ".jpg"
        else:
            base_directory = self.videos_dir
            prefix = "vid_"
            extension = ".mp4"

        # date folder (YYYY-MM-DD)
        date_folder = self.create_datestamp()
        directory = base_directory / date_folder
        directory.mkdir(parents=True, exist_ok=True)

        filename = prefix + self.create_timestamp() + extension
        return directory / filename


    def create_mock_file(self, file_type):
        mock_file_path = self.build_media_path(file_type)

        with open(mock_file_path, "a"):
            pass

        return mock_file_path
