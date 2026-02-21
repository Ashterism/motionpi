def detect_runmode():
    try:
        with open("/proc/device-tree/model") as f:
            if "Raspberry Pi" in f.read():
                return "prod"
    except Exception:
        pass
    return "dev"