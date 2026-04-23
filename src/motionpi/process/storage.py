import json, shutil

from datetime import datetime
from pathlib import Path


class Storage:
    def __init__(self):
        # save directories into temp memory)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.data_dir = base_dir / "data"  # /data directory (e.g /lapsepi/data)
        self.single_img_dir = self.data_dir / "images"
        self.session_dir = self.data_dir / "sessions"  # taken images directory
        self.videos_dir = self.data_dir / "videos"  # recorded video directory
        self.meta_dir = self.data_dir / "meta"  # metadata directory

    # HELPERS
    def create_timestamp(self):
        return datetime.now().strftime("%H-%M-%S")

    def create_datestamp(self):
        return datetime.now().strftime("%Y-%m-%d")

    # CREATE FOLDER PATHS
    def build_folder_path(self, session_type):
        if session_type == "single_image":
            directory = self.single_img_dir
        elif session_type == "timelapse":
            base_directory = self.session_dir

            # date folder (YYYY-MM-DD)
            date_folder = self.create_datestamp()
            time_folder = self.create_timestamp()
            directory = base_directory / date_folder / time_folder

        directory.mkdir(parents=True, exist_ok=True)
        return directory

    # CREATE FILE PATH
    def build_image_filepath(self, directory):
        prefix = "img_"
        extension = ".jpg"

        filename = prefix + self.create_timestamp() + extension
        return directory / filename

    # READ / WRITE JSON
    def write_json(self, file_path, content):
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as json_file:
            json.dump(content, json_file)

    def read_json(self, file_path):
        if not file_path.exists():
            return None
        with open(file_path, "r") as json_file:
            return json.load(json_file)

    def delete_file(self, file_path):
        if file_path.exists() and file_path.is_file():
            file_path.unlink()

    # LOCKFILE HANDLING
    def create_lockfile(self, name):
        lock_path = self.meta_dir / f"{name}.lock"
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        with open(lock_path, "w"):
            pass

    def check_lockfile(self, name):
        lock_path = self.meta_dir / f"{name}.lock"
        return lock_path.exists()

    def delete_lockfile(self, name):
        lock_path = self.meta_dir / f"{name}.lock"
        if lock_path.exists():
            lock_path.unlink()

    # CLEAR IMAGES
    def clear_directory(self, directory):
        if not directory.exists():
            return
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    def clear_images(self):
        self.clear_directory(self.single_img_dir)

    def clear_sessions(self):
        self.clear_directory(self.session_dir)

    def clear_all_media(self):
        self.clear_images()
        self.clear_sessions()


    # Make media findable and accessible

    def list_sessions(self):
        sessions = []

        if not self.session_dir.exists():
            return sessions
        
        # iterate date folders
        for date_dir in sorted(self.session_dir.iterdir(),reverse=True):
            if not date_dir.is_dir():
                continue

            # iterate time folders in each date
            for time_dir in sorted(date_dir.iterdir(), reverse=True):
                if not time_dir.is_dir():
                    continue

                # relative path for FE
                rel_path = time_dir.relative_to(self.data_dir)


                # simple display label
                label = f"{date_dir.name} {time_dir.name.replace('-',':')}"
                sessions.append({
                    "path": str(rel_path),
                    "label": label
                })

        return sessions

        
    def list_session_media(self, session_path):
        media = []

        if not session_path:
            return media

        session_dir = self.data_dir / session_path

        if not session_dir.exists() or not session_dir.is_dir():
            return media

        for item in sorted(session_dir.iterdir()):
            if not item.is_file():
                continue

            if item.suffix.lower() != ".jpg":
                continue

            rel_path = item.relative_to(self.data_dir)
            label = item.stem.replace("img_", "").replace("-", ":")

            media.append({
                "path": str(rel_path),
                "label": label,
            })

        return media


    def list_timelapse_vids(self):
        videos = []

        if not self.session_dir.exists():
            return videos

        for date_dir in sorted(self.session_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue

            for time_dir in sorted(date_dir.iterdir(), reverse=True):
                if not time_dir.is_dir():
                    continue

                for item in sorted(time_dir.iterdir()):
                    if not item.is_file():
                        continue

                    if item.suffix.lower() != ".mp4":
                        continue

                    rel_path = item.relative_to(self.data_dir)
                    session_rel_path = time_dir.relative_to(self.data_dir)
                    session_label = f"{date_dir.name} {time_dir.name.replace('-', ':')}"

                    videos.append({
                        "path": str(rel_path),
                        "label": f"{session_label} - {item.name}",
                        "session_path": str(session_rel_path),
                        "session_label": session_label,
                        "filename": item.name,
                    })

        return videos



