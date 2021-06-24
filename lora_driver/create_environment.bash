#!/bin/bash

echo "Removing prev. made .env"
rm -rf .env

echo "Creating env"
python3 -m venv .env

echo "Activating env"
source .env/bin/activate

echo "Installing packages"
pip3 install adafruit-circuitpython-rfm9x
pip3 install -e "git+https://github.com/google/flatbuffers@df2df21ec1be2468106fed10c1533eacc1cf0d2e#egg=flatbuffers&subdirectory=python"
