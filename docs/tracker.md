# LoRa GPS Tracker

Our LoRa GPS trackers are based on the [TTGO T-Beam from LilyGO](https://www.tinytronics.nl/shop/en/communication/gps/lilygo-ttgo-t-beam-v1.0-lora-868mhz-neo-6m-gps-esp32), which is an ESP32
development board with built-in GPS & LoRa modems, along with a battery holder & charger. 

The code in `tracker_firmware` is made to run on those GPS trackers, but also has compatability for the [DOIT ESP32 DevKit V1](https://www.tinytronics.nl/shop/en/development-boards/microcontroller-boards/with-wi-fi/esp32-wifi-and-bluetooth-board-cp2102). These can be used as non-tracker LoRa mesh nodes which can help expand the LoRa mesh network.

## Mock GPS Mode

Because we were having trouble getting a GPS fix inside of buildings with the TTGO T-Beam hardware, we added a mock GPS mode which can be activated by quickly pressing the IO38 button twice. Pressing it twice again will disable the mock-GPS mode.

## Setting up workspace

The code is setup as a [PlatformIO](https://platformio.org/) project, which means you will need to follow the [PlatformIO getting started guide](https://docs.platformio.org/en/latest/integration/ide/pioide.html) to get your workspace setup.

Next, we should initialize the workspace for the IDE of your choice, using `pio project init`. Because this project can be built for several kinds of hardware targets, we will need to specify the correct "environment":

|name|description|
|---|---|
|`DEVICE-1-T`|LoRa GPS tracker with Node ID 10|
|`DEVICE-2-O`|Generic LoRa node with Node ID 11|
|`DEVICE-3-O`|Generic LoRa node with Node ID 12|

For example:
```
platformio project init --ide vscode -e DEVICE-1-T
```

Once this is setup, we can install the libraries used by this project:

```
platformio lib install -e DEVICE-1-T
```

## Building & uploading the firmware

After we have our workspace setup, we can build & upload our firmware to our device. To do so, use `platformio run` (again, with the preferred environment):

```
platformio run --target upload -e DEVICE-1-T
```