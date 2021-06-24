import struct as s
from array import array


class MeshMessageHeader:
    def __init__(self, msg_type):
        self.msg_type = msg_type

    @staticmethod
    def get_struct():
        return s.Struct('B')

    @classmethod
    def from_bytes(cls, data: bytearray):
        u = MeshMessageHeader.get_struct().unpack(data)

        return cls(
            msg_type=u[0]
        )

    @classmethod
    def from_new(cls, msg_type):
        return cls(
            msg_type=msg_type
        )

    def to_bytes(self):
        return MeshMessageHeader.get_struct().pack(
            self.msg_type
        )
    
    def to_dict(self):
        return {
            "msg_type": self.msg_type
        }


class MeshApplicationMessage:
    def __init__(self, header: MeshMessageHeader, data):
        self.header = header
        self.data = data

    @staticmethod
    def get_struct(message_size: int):
        return s.Struct('{}s{}B'.format(
            MeshMessageHeader.get_struct().size,
            message_size - MeshMessageHeader.get_struct().size
        ))

    @classmethod
    def from_bytes(cls, data: bytearray):
        u = MeshApplicationMessage.get_struct(len(data)).unpack(data)

        return cls(
            header=MeshMessageHeader.from_bytes(u[0]),
            data=u[1::]
        )

    @classmethod
    def from_new(cls, header: MeshMessageHeader, data: bytearray):
        return cls(
            header=header,
            data=data
        )

    def to_bytes(self):
        header = self.header.to_bytes()
        return MeshApplicationMessage.get_struct(len(header) + len(self.data)).pack(header, *self.data)
    
    def to_dict(self):
        return {
            "header": self.header.to_dict(),
            "data": self.data
        }


class RoutedMessageHeader:
    def __init__(self, dest, source, hops, idd, flags):
        self.dest = dest
        self.source = source
        self.hops = hops
        self.id = idd
        self.flags = flags

    @staticmethod
    def get_struct():
        return s.Struct('BBBBB')

    @classmethod
    def from_bytes(cls, data: bytearray):
        u = RoutedMessageHeader.get_struct().unpack(data)

        return cls(
            dest=u[0],
            source=u[1],
            hops=u[2],
            idd=u[3],
            flags=u[4],
        )

    @classmethod
    def from_new(cls, dest, source, hops, idd, flags):
        return cls(
            dest=dest,
            source=source,
            hops=hops,
            idd=idd,
            flags=flags
        )

    def to_bytes(self):
        return RoutedMessageHeader.get_struct().pack(
            self.dest, self.source, self.hops, self.id, self.flags
        )

    def to_dict(self):
        return {
            "dest": self.dest,
            "source": self.source,
            "hops": self.hops,
            "id": self.id,
            "flags": self.flags
        }


class RoutedMessage:
    def __init__(self, header: RoutedMessageHeader, data: MeshApplicationMessage):
        self.header = header
        self.data = data

    @staticmethod
    def get_struct(message_size: int):
        return s.Struct('{}s{}B'.format(
            RoutedMessageHeader.get_struct().size,
            message_size - RoutedMessageHeader.get_struct().size,))

    @classmethod
    def from_bytes(cls, data: bytearray):
        u = RoutedMessage.get_struct(len(data)).unpack(data)

        return cls(
            header=RoutedMessageHeader.from_bytes(u[0]),
            data=MeshApplicationMessage.from_bytes(array('B', u[1::]))  # data,
        )

    @classmethod
    def from_new(cls, header: RoutedMessageHeader, data: MeshApplicationMessage):
        return cls(
            header=header,
            data=data
        )

    def to_bytes(self):
        header = self.header.to_bytes()
        data = self.data.to_bytes()
        return RoutedMessage.get_struct(len(header) + len(data)).pack(header, *data)

    def to_dict(self):
        return {
            "header": self.header.to_dict(),
            "data": self.data.to_dict()
        }
