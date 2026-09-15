import shutil
import socket
import subprocess

from flask import (
    Flask,
    render_template,
    send_from_directory,
    redirect,
    jsonify,
    request,
)

from ..control.controller import (
    get_photo,
    get_timelapse,
    get_timelapse_stopped,
    get_timelapse_video,
    get_sensor_state,
    set_sensor_state,
    get_settings_options,
    get_settings,
    update_settings,
)
from ..process.storage import Storage
from ..process.network_admin import get_network_manager

storage = Storage()

app = Flask(__name__)


@app.context_processor
def device_context():
    return {"device_name": socket.gethostname()}


# route to homepage
@app.route("/")
def home():
    last_image_record = storage.read_json(storage.meta_dir / "last_image_taken.json")

    image_path = "/static/imgs/no_image.png"
    taken_time = "-"

    if last_image_record:
        file_location = last_image_record.get("file_location")
        raw_time = last_image_record.get("last_updated")

        if file_location:
            actual_image_path = storage.data_dir / file_location

            if actual_image_path.exists():
                image_path = f"/data/{file_location}"

                if raw_time:
                    from datetime import datetime

                    dt = datetime.strptime(raw_time, "%Y-%m-%d_%H-%M-%S")
                    taken_time = dt.strftime("%y/%m/%d %H:%M:%S")

    is_running = storage.check_lockfile("camera_in_use")
    motion_sensor_state = get_sensor_state()

    return render_template(
        "index.html",
        image_path=image_path,
        taken_time=taken_time,
        is_running=is_running,
        motion_sensor_state=motion_sensor_state,
    )


# Serve media from /data
@app.route("/data/<path:filename>")
def serve_media(filename):
    return send_from_directory(
        storage.data_dir,
        filename,
        mimetype="video/mp4" if filename.endswith(".mp4") else None,
        conditional=True,
    )


# route to check if camera in use (lockfile check)
@app.route("/status")
def status():
    is_running = storage.check_lockfile("camera_in_use")
    state = "RUNNING" if is_running else "IDLE"

    return jsonify(
        {
            "state": state,
            "latest_frame": None,
            "frames_taken": None,
        }
    )


# route to call "take single image" function
@app.route("/take_photo", methods=["POST"])
def take_photo():
    get_photo()
    return redirect("/")


# route to set motion sensor state
@app.route("/motion_sensor", methods=["POST"])
def motion_sensor():
    state = request.form.get("motion-sensor")
    set_sensor_state(state)
    return redirect("/")


# route to call get timelapse (which runs in own process)
@app.route("/take_timelapse", methods=["POST"])
def take_timelapse():
    interval = request.form.get("interval")
    runtime = request.form.get("runtime")

    get_timelapse(interval, runtime)
    return redirect("/")


# route to kill the timelapse process
@app.route("/stop_timelapse", methods=["POST"])
def stop_timelapse():
    get_timelapse_stopped()
    return redirect("/")


@app.route("/gallery")
def gallery():
    sessions = storage.list_sessions()
    selected_session = request.args.get("session")
    session_media = storage.list_session_media(selected_session)

    timelapse_videos = storage.list_timelapse_vids()

    return render_template(
        "gallery.html",
        sessions=sessions,
        selected_session=selected_session,
        session_media=session_media,
        timelapse_videos=timelapse_videos,
    )


@app.route("/create_video", methods=["POST"])
def create_video():
    session_path = request.form.get("session")
    fps = int(request.form.get("fps"))

    get_timelapse_video(session_path, fps)

    return redirect(f"/gallery?session={session_path}")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        update_settings(request.form)
        return redirect("/settings")

    return render_template(
        "settings.html",
        settings_options=get_settings_options(),
        current_settings=get_settings(),
    )


@app.route("/network")
def network_admin():
    try:
        manager = get_network_manager()
        saved_mode = manager.get_network_mode().get("mode", "hotspot")

        return render_template(
            "network.html",
            error=None,
            network_options=manager.get_network_options(),
            saved_mode=saved_mode,
            current_mode=manager.get_current_network_mode(),
            networks=manager.get_saved_wifi_networks(),
        )
    except Exception as exc:
        return render_template(
            "network.html",
            error=str(exc),
            network_options={"modes": {}},
            saved_mode="unknown",
            current_mode="unknown",
            networks=[],
        )


@app.route("/network/mode", methods=["POST"])
def network_mode():
    manager = get_network_manager()
    manager.update_network_settings(request.form)
    return redirect("/network")


@app.route("/network/forget", methods=["POST"])
def network_forget():
    manager = get_network_manager()
    manager.forget_wifi_network(request.form.get("connection_name", ""))
    return redirect("/network")


@app.route("/network/add", methods=["POST"])
def network_add():
    manager = get_network_manager()
    manager.add_wifi_network(
        request.form.get("ssid", ""),
        request.form.get("password", ""),
    )
    return redirect("/network")


@app.route("/device/reboot", methods=["POST"])
def device_reboot():
    systemctl = shutil.which("systemctl") or "/usr/bin/systemctl"

    permission_check = subprocess.run(
        ["sudo", "-n", "-l", systemctl, "reboot"],
        capture_output=True,
        text=True,
    )

    if permission_check.returncode != 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Motionpi does not have non-interactive permission to reboot this device.",
                }
            ),
            503,
        )

    subprocess.Popen(
        ["sudo", "-n", systemctl, "reboot"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    return jsonify({"ok": True, "message": "Reboot started"}), 202


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)


"""
python -m motionpi.web.app
"""
