@echo off

echo Removing prev. made .env
rmdir /Q /S .env

echo Creating env
python -m venv .env

echo Installing packages
.env\Scripts\pip3.exe install adafruit-circuitpython-rfm9x
.env\Scripts\pip3.exe install -e "git+https://github.com/google/flatbuffers@df2df21ec1be2468106fed10c1533eacc1cf0d2e#egg=flatbuffers&subdirectory=python"
