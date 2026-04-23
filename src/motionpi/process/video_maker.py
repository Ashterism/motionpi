# This file takes a folder of images from a timelapse session and turns them into an MP4 using ffmpeg.
#
# Python does the orchestration:
# 1. Get the ordered list of images for a session
# 2. Write them into a temporary concat file ffmpeg can read
# 3. Run ffmpeg via subprocess
# 4. Validate the output file
# 5. Clean up the temp file

import subprocess

from .storage import Storage

storage = Storage()


def create_timelapse_video(session_path, fps=30):
    if not session_path:
        return None

    session_dir = storage.data_dir / session_path

    if not session_dir.exists() or not session_dir.is_dir():
        return None

    media = storage.list_session_media(session_path)

    if not media:
        return None
    
    session_time = session_dir.name           # 13-48-46
    session_date = session_dir.parent.name    # 2026-04-21

    filename = f"lapse{session_date[2:].replace('-', '')}_{session_time[:5].replace('-', '')}.mp4"

    output_path = session_dir / filename
    file_list_path = session_dir / "file_list.txt"

    frame_duration = 1 / fps

    try:
        with open(file_list_path, "w", encoding="utf-8") as f:
            for item in media:
                img_path = storage.data_dir / item["path"]
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {frame_duration}\n")

            # Repeat the last frame so ffmpeg applies the final duration.
            last_img_path = storage.data_dir / media[-1]["path"]
            f.write(f"file '{last_img_path}'\n")

            command = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(file_list_path),
                "-fps_mode",
                "vfr",
                "-c:v", 
                "libx264",
                "-vf", 
                "scale=1280:-2",
                "-pix_fmt", 
                "yuv420p",
                "-movflags", 
                "+faststart",
                str(output_path),
            ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("ffmpeg returned non-zero exit code")
            print("returncode:", result.returncode)
            print("command:", " ".join(command))
            print("stderr:", result.stderr)

        # Only treat as failure if no valid output file exists
        if not output_path.exists() or output_path.stat().st_size <= 1024:
            print("ffmpeg did not create a valid output file")
            print("command:", " ".join(command))
            print("stderr:", result.stderr)
            if output_path.exists():
                output_path.unlink()
            return None

        return str(output_path)

    finally:
        if file_list_path.exists():
            file_list_path.unlink()