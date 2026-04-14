"""
TelemetryStore — thread-safe cache of the most-recent parsed telemetry
objects for each topic.

The broker's dispatch loop runs in the asyncio thread; the Archon
actor system and GUI code also run in asyncio.  Reads and writes are
therefore always on the same thread, so no locking is strictly
required.  We provide a simple dataclass-style API for clarity.

Usage::

    store = TelemetryStore()
    # broker calls:
    store.tcs = TcsTelemetry(...)
    # consumer reads:
    par = store.tcs.CurrentParAngle if store.tcs else None
"""

from dataclasses import dataclass, field

from .models.tcs_telemetry import TcsTelemetry
from .models.tcs_status import TcsStatus
from .models.wrs_telemetry import WrsTelemetry
from .models.wilds_telemetry import WildsTelemetry


@dataclass
class TelemetryStore:
    """
    Holds the latest parsed telemetry received from the broker.

    All fields are None until the first message of that type arrives.
    All fields are updated atomically (single Python assignment) so
    consumers always see a consistent snapshot of the most recent frame.
    """

    tcs: TcsTelemetry | None = field(default=None)
    """Latest tcs.loisTelemetry frame (~2 Hz)."""

    tcs_status: TcsStatus | None = field(default=None)
    """Latest TCSTcsStatusSV frame (~1 Hz)."""

    wrs: WrsTelemetry | None = field(default=None)
    """Latest wrs.loisTelemetry frame (~1 Hz)."""

    wilds: WildsTelemetry | None = field(default=None)
    """Latest wilds.loisTelemetry frame (our own output, echoed back)."""

    def clear(self) -> None:
        """Reset all cached values (e.g. on broker reconnect)."""
        self.tcs = None
        self.tcs_status = None
        self.wrs = None
        self.wilds = None
