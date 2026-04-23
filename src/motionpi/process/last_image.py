from pathlib import Path
from .storage import Storage

storage = Storage()


def update_last_image_taken(content):
    storage.meta_dir.mkdir(parents=True, exist_ok=True)
    file_path = storage.meta_dir / "last_image_taken.json"

    datestamp = storage.create_datestamp() + "_" + storage.create_timestamp()

    # store path relative to images_dir for portability
    relative_path = Path(content).relative_to(storage.data_dir)

    full_content = {
        "last_updated": datestamp,
        "file_location": str(relative_path),
    }

    storage.write_json(file_path, full_content)


def read_last_image_taken():
    file_path = storage.meta_dir / "last_image_taken.json"
    data = storage.read_json(file_path)

    if not data:
        return None

    return data.get("file_location")
