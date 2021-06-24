from flatbuffers import flexbuffers as flex
import zlib

class WackyFlatbufferEncodingError(Exception):
    pass
class WackyFlatbufferDecodingError(Exception):
    pass


class WackyFlatbuffers:
    @staticmethod
    def decode(data: str, with_zlib=True) -> dict:
        try:
            data = bytearray.fromhex(data)
            if with_zlib:
                return flex.Loads(zlib.decompress(data))
            return flex.Loads(data)
        except:
            raise WackyFlatbufferDecodingError()

    @staticmethod
    def encode(data: dict, with_zlib=True) -> str:
        try:
            buf = flex.Dumps(data)
            if with_zlib:
                return zlib.compress(buf)
            return buf
        except:
            raise WackyFlatbufferEncodingError()
