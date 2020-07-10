import pytest

from arpq import (
    JSONEncoder,
    UJSONEncoder,
    PickleEncoder,
    MarshalEncoder,
    MSGPACKEncoder,
)


@pytest.mark.parametrize(
    "encoder",
    [JSONEncoder, UJSONEncoder, MSGPACKEncoder, MarshalEncoder, PickleEncoder],
)
def test_encoders_basic(encoder):
    data = dict(
        int=42, str="Hello World", float=3.14, list=[1, 2, 3], dict={"13": "37"}
    )
    instace = encoder()

    encoded = instace.encode(data)

    assert data == instace.decode(encoded)
