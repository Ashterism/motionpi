# Motionpi

A lightweight Raspberry Pi motion-triggered camera using the Raspberry Pi Camera Module and a PIR sensor.

Remember to activate the virtual environment before running Motionpi:

```bash
source .venv/bin/activate
```

## Hardware

- Raspberry Pi Camera Module 3 NoIR (Wide)
- Raspberry Pi PIR Camera Case
- HC-SR501 (or compatible) PIR sensor

![PIR board](../../.readme_imgs/pir_board.png)

### PIR calibration

Use:

```text
src/motionpi/utils/pir_calibration.py
```

Adjust the onboard potentiometers:

- Anti-clockwise: decrease
- Clockwise: increase

---

# Installation

## Initial Pi setup

Install Raspberry Pi OS (64-bit), then update the system:

```bash
sudo apt update
sudo apt upgrade -y
```

A reboot afterwards is recommended.

## Install system packages

Install Python, the Raspberry Pi camera stack, GPIO support and ffmpeg:

```bash
sudo apt install -y \
    git \
    python3-venv \
    python3-pip \
    python3-picamera2 \
    python3-rpi.gpio \
    ffmpeg
```

## Clone the repository

```bash
git clone https://github.com/Ashterism/motionpi.git
cd motionpi
```

## Create a virtual environment

`picamera2` and `RPi.GPIO` are installed by Raspberry Pi OS rather than pip, so create the virtual environment with access to the system packages:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

## Install Motionpi

```bash
pip install --upgrade pip
pip install -e .
```

## Run

```bash
python -m motionpi
```

## Install as a systemd service

Copy the service file:

```bash
sudo cp src/motionpi/utils/motionpi.service /etc/systemd/system/motionpi.service
```

Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable motionpi.service
sudo systemctl start motionpi.service
```

Check it's running:

```bash
systemctl status motionpi.service
```

View the logs:

```bash
journalctl -u motionpi.service -f
```