import socket
import logging
from helper_modules.activity_leds import ActivityLeds
from board_config import *
from openremote_modules.exceptions import *




class NetworkHandler:
    def __init__(self,
                 tcp_addr: str,
                 tcp_port: int,
                 buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self.__activity_leds = ActivityLeds()
        self.__buffer_size = buffer_size
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((tcp_addr, tcp_port))
        self.__current_connection = None
        self.__sock.settimeout(1)
        self.__logger = logging.getLogger(__name__)
    
    def is_connection_open(self):
        return self.__current_connection is not None
            

    def cleanup(self, only_current_connection=False):
        if self.__current_connection is not None and only_current_connection:
            self.__logger.warning("Closing current connection.")
            self.__current_connection.close()
            self.__current_connection = None
        
        if not only_current_connection:
            self.__logger.info("Closing main socket!")
            self.__sock.close()

    def start_listening(self) -> bool:
        self.__sock.listen(1)
        self.__sock.settimeout(1)
        try:
            connection, address = self.__sock.accept()
            self.__logger.info("Accepted connection from '%s'", address)
            self.__current_connection = connection
            return True
        except socket.timeout:
            return False

    def receive_buffer(self):
        if not self.is_connection_open():
            raise NoConnectionIsOpenException()

        try:
            received_data = self.__current_connection.recv(self.__buffer_size)
            self.__activity_leds.blink_daemon_rx()
            return received_data
        except Exception as e:
            self.__current_connection = None
            raise NetworkHandlerReceivingException(e)

    def send_to_current_connection(self, data: bytes):
        if not self.is_connection_open():
            raise NoConnectionIsOpenException()
        self.__logger.debug(f"Sending '{data}' to the current connection!")

        try:
            sent_len = self.__current_connection.send(
                data# + b'\n'
            )
            self.__activity_leds.blink_daemon_tx()
            return sent_len
        except BrokenPipeError:
            self.__current_connection = None
            raise NetworkHandlerSendingException()
            