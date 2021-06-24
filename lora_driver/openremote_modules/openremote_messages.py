import json
from enum import Enum


class OpenRemoteMessageTypes(Enum):
    """
    Message types which both sides recognize
    """
    ERROR = "ERROR"
    HANDSHAKE = "HANDSHAKE"
    CONFIGURE = "CONFIGURE"
    CONFIGURE_OK = "CONFIGURE_OK"
    RECEIVED_MESSAGE = "RECEIVED_MESSAGE"


class OpenRemoteMessage:
    """
    The most basic OR message which does not have extra data
    """
    def __init__(self, type: OpenRemoteMessageTypes) -> None:
        self.type = type

    @classmethod
    def from_bytes(cls, data: bytes):
        """Creates class from bytes

        Args:
            data (bytes): Encoded json string

        Returns:
            OpenRemoteMessage: Class with data from the input
        """
        data = json.loads(data)
        return cls(
            type=OpenRemoteMessageTypes[data["type"]
                                        ] if "type" in data else None
        )

    @classmethod
    def from_new(cls, type: OpenRemoteMessageTypes):
        """Creates a fresh new class

        Args:
            type (OpenRemoteMessageTypes): Custom message type

        Returns:
            OpenRemoteMessage: Class with the type provided
        """
        return cls(type=type)

    def to_dict(self):
        """Converts the class to (dict) object

        Returns:
            [dict]: Dict with the class content (type)
        """
        print(self.type)
        return {
            "type": self.type.name
        }

    def to_bytes(self):
        """Converts the class to (dict) and then to json string bytes

        Returns:
            [bytes]: Encoded json string representation of the class
        """
        return json.dumps(self.to_dict()).encode("UTF-8")


class OpenRemoteReceivedMessageMessage:
    """
    OpenRemote ReceivedMessage Message containing:
    - LoRa sender ID
    - Data sent
    - And the message type = [OpenRemoteMessageTypes.RECEIVED_MESSAGE]
    """
    def __init__(self, from_id: int, data: dict) -> None:
        self.from_id = from_id
        self.data = data
        self.type = OpenRemoteMessageTypes.RECEIVED_MESSAGE

    @classmethod
    def from_new(cls, from_id: int, data: dict):
        """Creates a fresh new class

        Args:
            from_id (int): The LoRa node which sent the message
            data (dict): The flatbuffer decoded data received from this node

        Returns:
            [OpenRemoteReceivedMessageMessage]: Class with the data provided
        """
        return cls(
            from_id=from_id,
            data=data
        )

    def to_dict(self):
        """Converts the class to (dict) format

        Returns:
            [dict]: Class in dict format
        """
        return {
            "type": self.type.name,
            "data": self.data,
            "from_id": self.from_id
        }

    def to_bytes(self):
        """Converts the class to (dict) and then to json string bytes

        Returns:
            [bytes]: Encoded json string representation of the class
        """
        return json.dumps(self.to_dict()).encode("UTF-8")


class OpenRemoteConfigureMessage:
    """
    OpenRemote Configure Message containing:
    - LoRa Frequency value in (float) format
    - LoRa Node ID in (int) format
    - Message type = [OpenRemoteMessageTypes.CONFIGURE]

    """
    def __init__(self, frequency: float, node_id: int) -> None:
        self.type = OpenRemoteMessageTypes.CONFIGURE
        self.frequency = frequency
        self.node_id = node_id

    @classmethod
    def from_bytes(cls, data: bytes):
        data = json.loads(data)
        return cls(
            frequency=data["frequency"] if "frequency" in data else None,
            node_id=data["node_id"] if "node_id" in data else None
        )


class OpenRemoteErrorMessage:
    """
    OpenRemote Error Message containing:
    - Error in (str) format
    """
    def __init__(self, error_msg: str) -> None:
        self.error_msg = error_msg

    @classmethod
    def from_bytes(cls, data: bytes):
        """Creates class from bytes

        Args:
            data (bytes): Encoded json string

        Returns:
            OpenRemoteMessage: Class with data from the input
        """
        data = json.loads(data)
        return cls(
            error_msg=data["error_msg"] if "error_msg" in data else None
        )

    @classmethod
    def from_new(cls, error_msg: str):
        """Creates a fresh new class

        Args:
            error_msg (str): Error message to include

        Returns:
            [OpenRemoteErrorMessage]: Class with the provided error message.
        """
        return cls(error_msg=error_msg)

    def to_dict(self):
        """Converts the class to (dict) format

        Returns:
            [dict]: Class in dict format
        """
        return {
            "type": OpenRemoteMessageTypes.ERROR.name,
            "error_msg": self.error_msg
        }

    def to_bytes(self):
        """Converts the class to (dict) and then to json string bytes

        Returns:
            [bytes]: Encoded json string representation of the class
        """
        return json.dumps(self.to_dict()).encode("UTF-8")
