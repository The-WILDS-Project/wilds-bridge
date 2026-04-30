"""
STOMP connection manager.

Owns the stomp.Connection, attaches BrokerListener, and provides
an async reconnect loop that runs until cancelled.

Reconnect flow:
  1. connect() establishes the initial connection and subscriptions.
  2. The BrokerListener.on_disconnected() callback puts (None, None) on
     the shared queue.
  3. LDTBroker._dispatch_loop() detects the sentinel and calls
     reconnect(), which tears down the old connection and retries.

Thread-safety:
  stomp.Connection methods (connect, subscribe, disconnect, send) are
  safe to call from any thread.  We only call them from the asyncio
  thread (via await run_in_executor for blocking connect) or from
  on_disconnected (which is already on the stomp thread, but the
  calls are non-blocking).
"""

import asyncio
import logging

import stomp

from .config import BrokerConfig
from .listener import BrokerListener

logger = logging.getLogger(__name__)


class BrokerConnection:
    """
    Wraps a stomp.Connection and handles connect / subscribe /
    reconnect for LDTBroker.
    """

    def __init__(self, config: BrokerConfig, listener: BrokerListener) -> None:
        self._cfg = config
        self._listener = listener
        self._conn: stomp.Connection | None = None

    # ------------------------------------------------------------------
    # Public API (called from asyncio thread)
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """
        Create a fresh stomp.Connection, attach the listener, and
        perform a blocking connect() in a thread-pool executor so the
        event loop is not blocked during TCP/SSL negotiation.
        """
        loop = asyncio.get_running_loop()
        self._conn = stomp.Connection(
            [(self._cfg.host, self._cfg.port)],
            reconnect_attempts_max=1,  # we handle reconnect ourselves; 0 means don't try at all in stomp.py
        )
        self._conn.set_listener("bridge", self._listener)
        await loop.run_in_executor(
            None,
            self._do_connect,
        )
        self._subscribe_all()

    async def reconnect(self) -> None:
        """
        Disconnect (best-effort) then re-connect after the configured
        sleep interval.
        """
        self._disconnect_silent()
        logger.info(
            "Reconnecting to %s:%s in %.1f s …",
            self._cfg.host,
            self._cfg.port,
            self._cfg.reconnect_sleep,
        )
        await asyncio.sleep(self._cfg.reconnect_sleep)
        await self.connect()

    def send(self, destination: str, body: str) -> None:
        """
        Publish a message on a STOMP topic.  Called from asyncio thread;
        stomp.send() is non-blocking.
        """
        if self._conn is None or not self._conn.is_connected():
            logger.warning("send() called but not connected — dropping message")
            return
        self._conn.send(destination=f"/topic/{destination}", body=body)

    def is_connected(self) -> bool:
        return self._conn is not None and self._conn.is_connected()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _do_connect(self) -> None:
        """Blocking STOMP connect — run in executor."""
        self._conn.connect(
            self._cfg.username,
            self._cfg.password,
            wait=True,
        )
        logger.info("STOMP connected to %s:%s", self._cfg.host, self._cfg.port)

    def _subscribe_all(self) -> None:
        for i, topic in enumerate(self._cfg.subscriptions):
            self._conn.subscribe(
                destination=f"/topic/{topic}",
                id=str(i),
                ack="auto",
            )
            logger.debug("Subscribed to /topic/%s", topic)

    def _disconnect_silent(self) -> None:
        if self._conn is not None:
            try:
                self._conn.disconnect()
            except Exception:
                pass
            self._conn = None
