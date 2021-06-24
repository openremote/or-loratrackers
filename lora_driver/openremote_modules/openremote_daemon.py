import logging
from typing import SupportsRound
from lora_modules.rh_structs import RoutedMessage
from board_config import *
from lora_modules.lora_wrapper import LoraWrapper
from openremote_modules.network_handler import NetworkHandler
from openremote_modules.openremote_messages import OpenRemoteConfigureMessage, OpenRemoteReceivedMessageMessage
from openremote_modules.openremote_messages import OpenRemoteErrorMessage
from openremote_modules.openremote_messages import OpenRemoteMessage
from openremote_modules.openremote_messages import OpenRemoteMessageTypes
from helper_modules.wacky_flatbuffers import WackyFlatbufferDecodingError, WackyFlatbuffers
from openremote_modules.exceptions import *


class OpenRemoteDaemon:
    def __init__(self,
                 openremote_addr: str = DEFAULT_TCP_ADDR,
                 openremote_port: int = DEFAULT_TCP_PORT) -> None:
        self.__logger = logging.getLogger(__name__)

        self.__logger.debug(
            "Initializing NetworkHandler, addr=%s, port=%d", openremote_addr, openremote_port)

        self.__network_handler = NetworkHandler(openremote_addr, openremote_port)

        self.__logger.debug("Initializing LoraWrapper!")
        self.__lora_handler = LoraWrapper(0)  # Defaults to node id 0

    def accept_new_connection(self) -> bool:

        self.__logger.info("Waiting for a new connection!")
        try:
            while True:
                if self.__network_handler.start_listening():
                    self.__logger.info("Accepted a new connection!")
                    return True
        except KeyboardInterrupt:
            exit()
        except Exception:
            return False

    def __parse_message(self, data_in: bytes):
        try:
            return OpenRemoteMessage.from_bytes(data_in)
        except:
            raise OpenRemoteDataIsInvalidException()

    def __handle_configuration_message(self, raw_message: bytes) -> None:

        configuration_message = OpenRemoteConfigureMessage.from_bytes(
            raw_message)
        if configuration_message.node_id is None:
            raise OpenRemoteDataIsInvalidException()
        if configuration_message.frequency is None:
            raise OpenRemoteDataIsInvalidException()

        self.__logger.info(
            f"Configuration specifies frequency: {configuration_message.frequency} and node id: {configuration_message.node_id}")
        self.__lora_handler.configure(
            configuration_message.node_id, configuration_message.frequency)

    def handle_handshake(self) -> bool:
        """
        Handles the handshake protocol,
        BLOCKING, returns only if the connection is broken of success
        """
        handshake_request_msg = OpenRemoteMessage.from_new(
            OpenRemoteMessageTypes.HANDSHAKE)

        self.__logger.info("Sending handshake request to the OR")

        self.__network_handler.send_to_current_connection(
            handshake_request_msg.to_bytes())

        configured = False
        try:
            while not configured:
                buf = self.__network_handler.receive_buffer()
                msg = self.__parse_message(buf)
                if msg is None:
                    self.__logger.error(
                        f"Could not decode message, message buffer: {buf}")
                    self.__network_handler.send_to_current_connection(
                        OpenRemoteErrorMessage.from_new(
                            f"Invalid message format!").to_bytes()
                    )
                    continue

                if msg.type == OpenRemoteMessageTypes.CONFIGURE:
                    self.__handle_configuration_message(buf)
                    self.__network_handler.send_to_current_connection(
                        OpenRemoteMessage.from_new(OpenRemoteMessageTypes.CONFIGURE_OK).to_bytes())
                    configured = True
                else:
                    self.__network_handler.send_to_current_connection(OpenRemoteErrorMessage.from_new(
                        f"Invalid message type! Expected '{OpenRemoteMessageTypes.CONFIGURE}' got {msg.type}").to_bytes())
        except NoConnectionIsOpenException as e:
            self.__logger.error(type(e))
        except OpenRemoteDataIsInvalidException as e:
            self.__network_handler.cleanup(True)
            self.__logger.error(type(e))
        except NetworkHandlerReceivingException as e:
            self.__logger.error(type(e))
        except NetworkHandlerSendingException as e:
            self.__logger.error(type(e))
        
        return configured

    def lora_handle_tick(self):
        """
        Main loop receiving and handling LoRa messages
        """
        received_data = self.__lora_handler.receive(True, True)
        received_with_rssi = self.__lora_handler.get_last_rssi()

        if received_data is None:
            return

        sender = received_data[0].header.source

        self.__logger.debug(
            f"Received: '{received_data[1]}' with rssi={received_with_rssi} source is {sender}")

        self.__logger.debug("Decoding using flatbuffers")

        try:
            deflatbuffered = WackyFlatbuffers.decode(received_data[1])
            self.__logger.info(deflatbuffered)
            self.__network_handler.send_to_current_connection(
                OpenRemoteReceivedMessageMessage.from_new(sender, deflatbuffered).to_bytes())
        except WackyFlatbufferDecodingError as e:
            self.__logger.error(f"Could not decode flatbuffers: {e}")
        except NetworkHandlerSendingException as e:
            self.__logger.error(type(e))
            