from typing import Any

from .abc import ABCEncoder

# TODO: a way to pass arguments to encoders
# TODO: try to maintain list of supported/unsupported types for each encoder

__all__ = (
    "JSONEncoder",
    "UJSONEncoder",
    "MSGPACKEncoder",
    "MarshalEncoder",
    "PickleEncoder",
)


class _Encoder(ABCEncoder):

    __slots__ = ("_encoder",)

    encoder_import: str

    def __init__(self) -> None:
        try:
            self._encoder = __import__(self.encoder_import)
        except ImportError as e:
            raise RuntimeError(f"Unable to initialize {self.__class__.__name__}: {e}")


class JSONEncoder(_Encoder):
    """
    JSON encoder. Uses built-in json library.

    Can only encode simple data types: ints, floats, strings, booleans, lists.
    """

    encoder_import = "json"

    def encode(self, data: Any) -> bytes:
        return self._encoder.dumps(data).encode()

    def decode(self, stream: bytes) -> Any:
        return self._encoder.loads(stream)


class UJSONEncoder(JSONEncoder):
    """
    JSON encoder. Uses ujson library.

    Can only encode simple data types: ints, floats, strings, booleans, lists.
    """

    encoder_import = "ujson"


class MSGPACKEncoder(_Encoder):
    """
    MSGPACK encoder. Uses msgpack library.

    Can only encode simple data types: ints, floats, strings, booleans, lists.
    """

    encoder_import = "msgpack"

    def encode(self, data: Any) -> bytes:
        return self._encoder.packb(data)

    def decode(self, stream: bytes) -> Any:
        return self._encoder.unpackb(stream)


class MarshalEncoder(_Encoder):
    """
    Marshal encoder. Uses built-in marshal library. Only use when communicating between
    python instances. May not work if different python versions are used.

    Can only encode simple data types: ints, floats, strings, booleans, lists.
    """

    encoder_import = "marshal"

    def encode(self, data: Any) -> bytes:
        return self._encoder.dumps(data)

    def decode(self, stream: bytes) -> Any:
        return self._encoder.loads(stream)


class PickleEncoder(MarshalEncoder):
    """
    Pickle encoder. Uses built-in pickle library. Only use when communicating between
    python instances.

    Can be used to encode complex python objects.
    """

    encoder_import = "pickle"
