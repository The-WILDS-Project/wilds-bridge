"""
LDTBroker — top-level async façade for the LDT ActiveMQ bridge.

Lifecycle::

    broker = LDTBroker(config)
    await broker.start()          # connect + begin dispatch loop
    ...
    # publish WILDS telemetry:
    await broker.publish_wilds_telemetry(wt)
    # send TCS offset command:
    await broker.send_tcs_command(TcsCommand.make_offset(-8.1, 12.0))
    ...
    await broker.stop()           # graceful shutdown

Dispatch loop:
  Reads (topic, body) tuples from the asyncio.Queue filled by
  BrokerListener.  On each message:
    1. Deduplication — drop JOE duplicate frames (sha256 of body,
       per-topic LRU cache of ``config.dedup_cache_size`` hashes).
    2. Parse — route to the correct pydantic-xml model.
    3. Store — update TelemetryStore.
    4. Callbacks — invoke any registered handlers.
  A (None, None) sentinel triggers reconnect.

Callbacks::

    @broker.on(TOPIC_TCS_TELEMETRY)
    async def handle_tcs(msg: TcsTelemetry) -> None:
        ...
"""

import asyncio
import hashlib
import logging
from collections import deque
from collections.abc import Awaitable, Callable

from .config import (
    TOPIC_AOS_DATA_PACKET,
    TOPIC_AOS_FOCUS_ABSOLUTE,
    TOPIC_AOS_FOCUS_CLEAR,
    TOPIC_AOS_FOCUS_RELATIVE,
    TOPIC_INSTRUMENT_CUBE,
    TOPIC_NEW_SCIENCE_TARGET,
    TOPIC_TCS_COMMAND,
    TOPIC_TCS_STATUS,
    TOPIC_TCS_TELEMETRY,
    TOPIC_WILDS_TELEMETRY,
    TOPIC_WRS_DATA_PACKET,
    TOPIC_WRS_TELEMETRY,
    BrokerConfig,
)
from .connection import BrokerConnection
from .listener import BrokerListener
from .models.aos_data_packet import AosDataPacket
from .models.instrument_cube_telemetry import InstrumentCubeTelemetry
from .models.tcs_command import (
    TcsAbsorbOffsetCommand,
    TcsClearOffsetCommand,
    TcsNewScienceTargetCommand,
    TcsOffsetCommand,
)
from .models.tcs_status import TcsStatus
from .models.tcs_telemetry import TcsTelemetry
from .models.wilds_telemetry import WildsTelemetry
from .models.wrs_data_packet import WrsDataPacket
from .models.wrs_telemetry import WrsTelemetry
from .store import TelemetryStore

TcsCommand = TcsOffsetCommand | TcsClearOffsetCommand | TcsAbsorbOffsetCommand

logger = logging.getLogger(__name__)

# Type alias for async message callbacks
MessageCallback = Callable[[object], Awaitable[None]]


class LDTBroker:
    """
    Async interface to the LDT ActiveMQ broker.

    Parameters
    ----------
    config:
        Connection parameters and subscription list.  Defaults connect
        to the WebRat test broker.
    store:
        Optional pre-created TelemetryStore.  A new one is created if
        not provided.
    """

    def __init__(
        self,
        config: BrokerConfig | None = None,
        store: TelemetryStore | None = None,
    ) -> None:
        self._cfg = config or BrokerConfig()
        self.store = store or TelemetryStore()

        # asyncio.Queue shared between the stomp thread and this loop
        self._queue: asyncio.Queue[tuple[str | None, str | None]] = asyncio.Queue()

        # Populated in start()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._listener: BrokerListener | None = None
        self._connection: BrokerConnection | None = None
        self._dispatch_task: asyncio.Task | None = None

        # Per-topic dedup caches: topic → deque of recent body hashes
        self._dedup: dict[str, deque[str]] = {}

        # Registered callbacks per topic
        self._callbacks: dict[str, list[MessageCallback]] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Connect to the broker and start the dispatch loop."""
        self._loop = asyncio.get_running_loop()
        self._listener = BrokerListener(self._loop, self._queue)
        self._connection = BrokerConnection(self._cfg, self._listener)
        await self._connection.connect()
        self._dispatch_task = asyncio.create_task(self._dispatch_loop(), name="ldt-broker-dispatch")
        logger.info("LDTBroker started")

    async def stop(self) -> None:
        """Cancel the dispatch loop and disconnect."""
        if task := self._dispatch_task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        if self._connection is not None:
            self._connection._disconnect_silent()
        logger.info("LDTBroker stopped")

    # ------------------------------------------------------------------
    # Publish / send
    # ------------------------------------------------------------------

    async def publish_wilds_telemetry(self, telemetry: WildsTelemetry) -> None:
        """Publish a WildsTelemetry frame to wilds.loisTelemetry."""
        body = telemetry.to_xml(encoding="unicode")
        assert self._connection is not None
        assert body is not None and isinstance(body, (str, bytes))
        self._connection.send(
            TOPIC_WILDS_TELEMETRY, body.decode() if isinstance(body, bytes) else body
        )

    async def send_tcs_command(self, command: TcsCommand) -> None:
        """Send a TCS offset command to TCSTcsCommandSV."""
        body = command.to_xml(encoding="unicode")
        assert self._connection is not None
        assert body is not None and isinstance(body, (str, bytes))
        self._connection.send(TOPIC_TCS_COMMAND, body.decode() if isinstance(body, bytes) else body)

    async def send_new_target(self, command: TcsNewScienceTargetCommand) -> None:
        """Send a new science target command to NewScienceTargetSV."""
        body = command.to_xml(encoding="unicode")
        assert self._connection is not None
        assert body is not None and isinstance(body, (str, bytes))
        self._connection.send(TOPIC_NEW_SCIENCE_TARGET, body.decode() if isinstance(body, bytes) else body)

    async def send_aos_focus_offset(self, meters: float, *, relative: bool = False) -> None:
        """Send an AOS focus offset command. Units: meters."""
        topic = TOPIC_AOS_FOCUS_RELATIVE if relative else TOPIC_AOS_FOCUS_ABSOLUTE
        assert self._connection is not None
        self._connection.send(topic, str(meters))

    async def send_aos_focus_clear(self) -> None:
        """Reset the AOS focus offset to zero."""
        assert self._connection is not None
        self._connection.send(TOPIC_AOS_FOCUS_CLEAR, "true")

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def on(self, topic: str) -> Callable[[MessageCallback], MessageCallback]:
        """
        Decorator that registers an async callback for a topic.

        The callback receives the parsed pydantic-xml model instance.

        Example::

            @broker.on(TOPIC_TCS_TELEMETRY)
            async def handle(msg: TcsTelemetry) -> None:
                print(msg.CurrentParAngle)
        """

        def decorator(fn: MessageCallback) -> MessageCallback:
            self._callbacks.setdefault(topic, []).append(fn)
            return fn

        return decorator

    def add_callback(self, topic: str, fn: MessageCallback) -> None:
        """Register an async callback programmatically."""
        self._callbacks.setdefault(topic, []).append(fn)

    # ------------------------------------------------------------------
    # Internal — dispatch loop
    # ------------------------------------------------------------------

    async def _dispatch_loop(self) -> None:
        """
        Main async loop: drain the queue, parse, store, invoke callbacks.
        Runs until cancelled.
        """
        assert self._connection is not None

        while True:
            try:
                topic, body = await self._queue.get()
            except asyncio.CancelledError:
                return

            # Reconnect sentinel
            if topic is None:
                logger.warning("Reconnect sentinel received")
                await self._connection.reconnect()
                continue

            if body is None:
                logger.warning("Received message with empty body on topic %s", topic)
                continue

            # Dedup
            if self._is_duplicate(topic, body):
                logger.debug("Dropped duplicate frame on %s", topic)
                continue

            # Parse
            parsed = self._parse(topic, body)
            if parsed is None:
                continue

            # Store
            self._update_store(topic, parsed)

            # Callbacks
            for cb in self._callbacks.get(topic, []):
                try:
                    await cb(parsed)
                except Exception:
                    logger.exception("Callback error on topic %s", topic)

    # ------------------------------------------------------------------
    # Internal — deduplication
    # ------------------------------------------------------------------

    def _is_duplicate(self, topic: str, body: str) -> bool:
        digest = hashlib.sha256(body.encode()).hexdigest()
        cache = self._dedup.setdefault(topic, deque(maxlen=self._cfg.dedup_cache_size))
        if digest in cache:
            return True
        cache.append(digest)
        return False

    # ------------------------------------------------------------------
    # Internal — parsing
    # ------------------------------------------------------------------

    def _parse(self, topic: str, body: str) -> object | None:
        """
        Parse raw XML body into a pydantic-xml model.
        Returns None and logs a warning on parse failure.
        """
        try:
            if topic == TOPIC_TCS_TELEMETRY:
                return TcsTelemetry.from_xml(body)
            if topic == TOPIC_TCS_STATUS:
                return TcsStatus.from_xml(body)
            if topic == TOPIC_WRS_TELEMETRY:
                return WrsTelemetry.from_xml(body)
            if topic == TOPIC_WRS_DATA_PACKET:
                return WrsDataPacket.from_xml(body)
            if topic == TOPIC_AOS_DATA_PACKET:
                return AosDataPacket.from_xml(body)
            if topic == TOPIC_INSTRUMENT_CUBE:
                return InstrumentCubeTelemetry.from_xml(body)
            if topic == TOPIC_WILDS_TELEMETRY:
                return WildsTelemetry.from_xml(body)
        except Exception:
            logger.warning("Failed to parse message on topic %s", topic, exc_info=True)
            return None

        # Unknown topic — pass through as raw string so callbacks can handle it
        return body

    # ------------------------------------------------------------------
    # Internal — store update
    # ------------------------------------------------------------------

    def _update_store(self, topic: str, parsed: object) -> None:
        if topic == TOPIC_TCS_TELEMETRY and isinstance(parsed, TcsTelemetry):
            self.store.tcs = parsed
        elif topic == TOPIC_TCS_STATUS and isinstance(parsed, TcsStatus):
            self.store.tcs_status = parsed
        elif topic == TOPIC_WRS_TELEMETRY and isinstance(parsed, WrsTelemetry):
            self.store.wrs = parsed
        elif topic == TOPIC_WRS_DATA_PACKET and isinstance(parsed, WrsDataPacket):
            self.store.wrs_packet = parsed
        elif topic == TOPIC_AOS_DATA_PACKET and isinstance(parsed, AosDataPacket):
            self.store.aos = parsed
        elif topic == TOPIC_INSTRUMENT_CUBE and isinstance(parsed, InstrumentCubeTelemetry):
            self.store.instrument_cube = parsed
        elif topic == TOPIC_WILDS_TELEMETRY and isinstance(parsed, WildsTelemetry):
            self.store.wilds = parsed
