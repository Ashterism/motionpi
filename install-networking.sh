#!/usr/bin/env bash
set -euo pipefail

GENIE_DIR="/tmp/pi-network-genie"
CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/pi-network-genie.yaml"

rm -rf "$GENIE_DIR"
git clone --depth 1 https://github.com/Ashterism/pi-network-genie.git "$GENIE_DIR"

sudo bash "$GENIE_DIR/install.sh" "$CONFIG_FILE"

cat <<'EOF'

Pi Network Genie has been installed for Motionpi.

Before rebooting, check the generated services with:
  systemctl cat pi-network-genie.service
  systemctl cat motionpi.service

Then reboot when ready:
  sudo reboot
EOF
