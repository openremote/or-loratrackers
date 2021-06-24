import busio
import logging
import digitalio
import adafruit_rfm9x
from board_config import *
from helper_modules.activity_leds import ActivityLeds
from typing import Optional
import lora_modules.rh_structs as rh
from adafruit_blinka.microcontroller.bcm283x.pin import Pin


class LoraWrapper:
    def __init__(self,
                 node_addr: int,
                 radio_freq_mhz: float = DEFAULT_RADIO_FREQ_MHZ,
                 cs_pin: digitalio.DigitalInOut = DEFAULT_CS,
                 reset_pin: digitalio.DigitalInOut = DEFAULT_RESET,
                 spi_mosi_pin: Pin = DEFAULT_MOSI,
                 spi_miso_pin: Pin = DEFAULT_MISO,
                 spi_clock_pin: Pin = DEFAULT_CLOCK,
                 baudrate: int = DEFAULT_BAUDRATE,
                 enable_crc: bool = True,
                 ack_delay: float = 0.1,
                 ) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__activity_leds = ActivityLeds()
        self.__spi_bus = busio.SPI(
            clock=spi_clock_pin,
            MOSI=spi_mosi_pin,
            MISO=spi_miso_pin
        )

        self.__radio = adafruit_rfm9x.RFM9x(
            spi=self.__spi_bus,
            cs=cs_pin,
            reset=reset_pin,
            frequency=radio_freq_mhz,
            baudrate=baudrate
        )

        self.__radio.enable_crc = enable_crc
        self.__radio.ack_delay = ack_delay
        self.__radio.node = node_addr

    def receive(self, with_ack: bool, with_header: bool) -> Optional[str]:
        packet = self.__radio.receive(
            with_ack=with_ack,
            with_header=with_header
        )

        if packet is None:
            return None

        self.__activity_leds.blink_lora_tx()

        try:
            routed_message = rh.RoutedMessage.from_bytes(packet[4:])

            if routed_message.data.header.msg_type == 1:
                self.__logger.debug("Responding with discovery response")
                if self.__handle_discovery_packet(routed_message):
                    return self.receive(with_ack, with_header)
                return None
            elif routed_message.data.header.msg_type == 0:
                self.__logger.debug("Decoding application message...")
                return [routed_message, self.__decode_application_message(routed_message)]
            else:
                self.__logger.error("Message type unknown, don't know how to interpret it!")
                return None
        except Exception as e:
            # TODO: Except specific exception happening when from_bytes fails
            self.__logger.error(e)
            return None

    def __handle_discovery_packet(self, packet: rh.RoutedMessage) -> bool:
        self.__logger.debug(f"Discovery packet: {packet.to_dict()}")
        packet.data.header.msg_type = 2
        self.__radio.destination = packet.header.source
        return self.__radio.send_with_ack(packet.to_bytes())
    
    def __decode_application_message(self, packet: rh.RoutedMessage) -> str:
        return ''.join(hex(c).replace('0x', '').upper().zfill(2) for c in packet.data.data)



    def get_last_rssi(self):
        return self.__radio.last_rssi

    def send_with_ack(self, data: rh.RoutedMessage, destination: int = 0xFF) -> bool:
        self.__radio.destination = destination
        return self.__radio.send_with_ack(data.to_bytes())

    def configure(self, node_id: int, frequency: float):
        self.__logger.debug(
            f"Setting node id to {node_id} and frequency to {frequency}")
        self.__radio.frequency_mhz = frequency
        self.__radio.node = node_id
