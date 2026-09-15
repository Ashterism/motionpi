import sys
from pathlib import Path


GENIE_ROOT = Path("/opt/pi-network-genie/src/pi-network-genie")
PROJECT_CONFIG = Path("/home/ash/motionpi/pi-network-genie.yaml")


def _read_project_config():
    values = {}

    if not PROJECT_CONFIG.exists():
        return values

    for raw_line in PROJECT_CONFIG.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def get_network_manager():
    if not GENIE_ROOT.exists():
        raise RuntimeError("Pi Network Genie is not installed in /opt/pi-network-genie")

    genie_path = str(GENIE_ROOT)
    if genie_path not in sys.path:
        sys.path.insert(0, genie_path)

    from network.manager import NetworkManager

    config = _read_project_config()
    device_name = config.get("device_name", "motionpi")
    hotspot_connection_name = config.get(
        "hotspot_connection_name",
        f"{device_name}-hotspot",
    )

    return NetworkManager(
        settings_dir=Path.home() / ".config" / "pi-network-genie",
        hotspot_connection_name=hotspot_connection_name,
    )
