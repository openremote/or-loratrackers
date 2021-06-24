# Wacky IoT: OpenRemote LoRa GPS Trackers

OpenRemote has asked us to connect a "wacky" IoT device to their IoT platform. 
After some brainstorming we came up with our concept: a GPS tracker which works via long-range radio (a.k.a. LoRa) technology. 
The GPS trackers communicate over LoRa in a mesh network and send their locations via an edge device to the cloud-hosted OpenRemote platform.

## Results

While a "wacky" use-case for LoRa technology, we were able to make the system function as designed. 
Using LoRa technology for the GPS tracker mesh network helps devices stay connected even at long ranges, while being battery efficient.

## GPS Tracker firmware

The firmware ran on our GPS trackers which make them obtain their location and transmit packets over LoRa.

**Code**: [tracker_firmware/](tracker_firmware/)

**Docs**: Coming soon...

## RFM95 LoRa driver/OpenRemote interface

User-space driver for the RFM95 LoRa module & TCP interface for OpenRemote.

**Code**: [lora_driver/](lora_driver/)

**Docs**: Coming soon...

## OpenRemote fork w/ LoRa agent

Fork of OpenRemote which includes a new LoRaAgent type.
The LoRaAgent will connect with the LoRa driver/interface to configure the LoRa module & receive messages.

**Code**: [OpenRemote fork](https://github.com/Raqbit/openremote/)

**Docs**: Coming soon...

## OpenRemote location groovy rule

Custom OpenRemote rule which takes the GPS location from the attribute bound to the LoRaAgent and updates the asset's location.

**Code**: [Groovy rule](https://github.com/Raqbit/openremote/blob/radio-protocol/test/src/main/resources/org/openremote/test/rules/TestRule.groovy)

**Docs**: Coming soon...
