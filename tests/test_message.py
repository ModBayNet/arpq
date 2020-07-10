from arpq import Message, MarshalEncoder


def test_creation():
    encoder = MarshalEncoder()

    channel = "queue:test"
    priority = 10
    data = dict(hello="world")
    data_encoded = encoder.encode(data)

    msg = Message._from_zpopmax([data_encoded, priority], encoder)

    assert priority == msg.priority
    assert data == msg.data

    msg = Message._from_bzpopmax([channel, data_encoded, priority], encoder)

    assert priority == msg.priority
    assert data == msg.data
