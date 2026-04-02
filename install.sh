#!/bin/bash
set -e

APP_DIR="$HOME/bus-edge"

echo "Updating system..."
sudo apt update

echo "Installing system packages..."
sudo apt install -y python3 python3-pip python3-venv python3-lgpio gpsd gpsd-tools

echo "Changing to app directory..."
cd "$APP_DIR"

echo "Removing old install venv if it exists..."
rm -rf venv

echo "Creating virtual environment with system site packages..."
python3 -m venv --system-site-packages venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Done."
echo "Run the app with:"
echo "source venv/bin/activate && python3 main.py"
