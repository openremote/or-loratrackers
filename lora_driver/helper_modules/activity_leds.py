import digitalio
from board_config import *
from time import sleep


class ActivityLeds:

    def __init__(self) -> None:
        self.leds = [digitalio.DigitalInOut(DEFAULT_RGB_1),
                     digitalio.DigitalInOut(DEFAULT_RGB_2),
                     digitalio.DigitalInOut(DEFAULT_RGB_3)]
        self.lora_rx = 0
        self.daemon_tx = 1
        self.daemon_rx = 1

        for led in self.leds:
            led.direction = digitalio.Direction.OUTPUT
            led.value = True
            sleep(0.05)
            led.value = False
    
    def __blink_led(self, led_id: int, blink_duration: float = 0.1):
        self.leds[led_id].value = True
        sleep(blink_duration)
        self.leds[led_id].value = False
    
    def blink_lora_tx(self):
        self.__blink_led(self.lora_rx)
    def blink_daemon_rx(self):
        self.__blink_led(self.daemon_rx)
    def blink_daemon_tx(self):
        self.__blink_led(self.daemon_tx)
