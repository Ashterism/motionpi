from motionpi.process.storage import Storage

storage = Storage()

storage.clear_all_media()
storage.delete_file(storage.meta_dir / "last_image_taken.json")