"""
stomp.py ConnectionListener that bridges the STOMP background thread
into the asyncio event loop.

stomp.py calls on_message() from its own receive thread.
We can't await anything there, so we use loop.call_soon_threadsafe()
to enqueue a coroutine-scheduling call onto the asyncio loop.

The broker picks messages off the queue and dispatches them.
"""

import asyncio
import logging

import stomp

logger = logging.getLogger(__name__)


class BrokerListener(stomp.ConnectionListener):
    """
    Receives STOMP frames in the stomp.py thread and forwards
    raw (topic, body) tuples to an asyncio.Queue for processing
    in the event loop.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue) -> None:
        self._loop = loop
        self._queue = queue

    def on_message(self, frame: stomp.utils.Frame) -> None:
        topic = frame.headers.get("destination", "")
        # Strip leading /topic/ prefix that ActiveMQ adds
        if topic.startswith("/topic/"):
            topic = topic[len("/topic/"):]
        body: str = frame.body
        self._loop.call_soon_threadsafe(self._queue.put_nowait, (topic, body))

    def on_error(self, frame: stomp.utils.Frame) -> None:
        logger.error("STOMP error frame: %s", frame.body)

    def on_disconnected(self) -> None:
        logger.warning("STOMP disconnected")
        # Signal the reconnect loop in connection.py by putting a sentinel
        self._loop.call_soon_threadsafe(self._queue.put_nowait, (None, None))

    def on_connected(self, frame: stomp.utils.Frame) -> None:
        logger.info("STOMP connected: %s", frame.headers)
