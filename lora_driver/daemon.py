import logging
from openremote_modules.openremote_daemon import OpenRemoteDaemon
from helper_modules import logger_config
from openremote_modules.exceptions import *
from lora_modules.lora_wrapper import LoraWrapper
import sys


def wait_for_or():
    connected = False
    while not connected:
        if or_daemon.accept_new_connection(): 
            connected = or_daemon.handle_handshake()

def is_standalone()-> bool:
    if len(sys.argv) - 1 < 1:
        return False
    return sys.argv[1] == "s"
    

if __name__ == "__main__":

    logger = logging.getLogger(__name__)

    print("""
      _           _____              __  __           _
     | |         |  __ \     /\     |  \/  |         | |
     | |     ___ | |__) |   /  \    | \  / | ___  ___| |__
     | |    / _ \|  _  /   / /\ \   | |\/| |/ _ \/ __| '_ \\
     | |___| (_) | | \ \  / ____ \  | |  | |  __/\__ \ | | |
     |______\___/|_|  \_\/_/    \_\ |_|  |_|\___||___/_| |_|
    """)

    if(is_standalone()):
        logger.info("Running in standalone mode!")

        lora_wrapper = LoraWrapper(0)
        lora_wrapper.configure(0, 868.0)
        while True:
            data = lora_wrapper.receive(True, True)
            if data is not None:
                rssi = lora_wrapper.get_last_rssi()

                logger.info(f"Received data with rssi {rssi}")
                logger.info(data)
    else:

        logger.info("Initializing OpenRemote daemon.")


        or_daemon = OpenRemoteDaemon("0.0.0.0")

        wait_for_or()
        while True:
            """This is the main program loop,
            when connection is gone, a new connection will be accepted
            """
            try:
                or_daemon.lora_handle_tick()
            except NoConnectionIsOpenException:
                logger.warn("No connection is open, accepting new connections!")
                wait_for_or()
