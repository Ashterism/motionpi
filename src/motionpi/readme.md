
Remember to use VENV:
```
source .venv/bin/activate
```


## Hardware


	Raspberry Pi Camera Module 3 NoIR - Wide-angle × 1
	PIR Camera Case for Raspberry Pi 4 × 1
	HC-SR501 style PIR

![PIR board](../../.readme_imgs/pir_board.png)


## Installation

### Initial set up of pi

Using Rasbian OS 64 list

```
sudo apt update
sudo apt upgrade -y
```

### Install system packages

After rebooting, install python, Camera stack (Bookworm), and PIR GPIO:
```
sudo apt install -y git python3-venv python3-pip
sudo apt install -y python3-picamera2
sudo apt install -y python3-rpi.gpio
```

### Clone repo

```
git clone https://github.com/ashterism/motionpi.git
```

### Create and activate venv
```
python3 -m venv .venv
source .venv/bin/activate
```

### Run (using /src and no project.toml yet)

```
PYTHONPATH=src python3 -m motionpi.motion_trigger
```

cd ~/motionpi && source .venv/bin/activate && PYTHONPATH=src python3 -m motionpi