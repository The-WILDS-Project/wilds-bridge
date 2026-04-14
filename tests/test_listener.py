"""
Unit tests for BrokerListener.

Verifies the thread-safe queue bridging without a real STOMP connection.
We call on_message() / on_disconnected() directly, simulating what
stomp.py would do from its receive thread.
"""

import asyncio
from unittest.mock import MagicMock

import pytest

from wilds.bridge.listener import BrokerListener


def make_frame(destination: str, body: str):
    """Build a minimal stomp frame mock."""
    frame = MagicMock()
    frame.headers = {"destination": destination}
    frame.body = body
    return frame


@pytest.fixture
def loop_and_queue():
    loop = asyncio.new_event_loop()
    queue: asyncio.Queue = asyncio.Queue()
    yield loop, queue
    loop.close()


@pytest.fixture
def listener(loop_and_queue):
    loop, queue = loop_and_queue
    return BrokerListener(loop, queue), loop, queue


class TestOnMessage:
    def test_message_enqueued(self, listener):
        bl, loop, queue = listener
        frame = make_frame("/topic/tcs.loisTelemetry", "<tcsTelemetry/>")
        bl.on_message(frame)
        topic, body = loop.run_until_complete(queue.get())
        assert topic == "tcs.loisTelemetry"
        assert body == "<tcsTelemetry/>"

    def test_topic_prefix_stripped(self, listener):
        bl, loop, queue = listener
        frame = make_frame("/topic/wrs.loisTelemetry", "<wrsTelemetry/>")
        bl.on_message(frame)
        topic, _ = loop.run_until_complete(queue.get())
        assert topic == "wrs.loisTelemetry"

    def test_no_prefix_topic_preserved(self, listener):
        bl, loop, queue = listener
        frame = make_frame("bare.topic", "<data/>")
        bl.on_message(frame)
        topic, _ = loop.run_until_complete(queue.get())
        assert topic == "bare.topic"

    def test_body_preserved_verbatim(self, listener):
        bl, loop, queue = listener
        body = "<foo>bar &amp; baz</foo>"
        frame = make_frame("/topic/x", body)
        bl.on_message(frame)
        _, received_body = loop.run_until_complete(queue.get())
        assert received_body == body

    def test_multiple_messages_fifo(self, listener):
        bl, loop, queue = listener
        for i in range(3):
            bl.on_message(make_frame("/topic/t", f"msg-{i}"))

        results = [loop.run_until_complete(queue.get()) for _ in range(3)]
        bodies = [b for _, b in results]
        assert bodies == ["msg-0", "msg-1", "msg-2"]


class TestOnDisconnected:
    def test_sentinel_enqueued(self, listener):
        bl, loop, queue = listener
        bl.on_disconnected()
        topic, body = loop.run_until_complete(queue.get())
        assert topic is None
        assert body is None

    def test_sentinel_after_messages(self, listener):
        bl, loop, queue = listener
        bl.on_message(make_frame("/topic/t", "real-message"))
        bl.on_disconnected()

        topic1, body1 = loop.run_until_complete(queue.get())
        topic2, body2 = loop.run_until_complete(queue.get())

        assert topic1 == "t"
        assert body1 == "real-message"
        assert topic2 is None
        assert body2 is None


class TestOnConnectedAndError:
    def test_on_connected_does_not_enqueue(self, listener):
        bl, loop, queue = listener
        frame = make_frame("", "")
        frame.headers = {"session": "abc"}
        bl.on_connected(frame)
        assert queue.empty()

    def test_on_error_does_not_enqueue(self, listener):
        bl, loop, queue = listener
        frame = MagicMock()
        frame.body = "some error"
        bl.on_error(frame)
        assert queue.empty()
