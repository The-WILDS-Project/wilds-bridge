"""
Focuser — high-level async facade for AOS focus commands and state.

Usage::

    focuser = Focuser(broker)

    await focuser.set_offset(0.000416)   # absolute, meters
    await focuser.adjust(-0.0001)        # relative, meters
    await focuser.clear()

    print(focuser.total_offset)          # meters, or None
"""

from .broker import LDTBroker


class Focuser:
    """
    Async facade for AOS focus control and state.

    Parameters
    ----------
    broker:
        Connected LDTBroker instance.
    """

    def __init__(self, broker: LDTBroker) -> None:
        self._broker = broker

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def set_offset(self, meters: float) -> None:
        """Set an absolute AOS focus offset (meters)."""
        await self._broker.send_aos_focus_offset(meters, relative=False)

    async def adjust(self, delta_meters: float) -> None:
        """Apply a relative AOS focus adjustment (meters)."""
        await self._broker.send_aos_focus_offset(delta_meters, relative=True)

    async def clear(self) -> None:
        """Reset the AOS focus offset to zero."""
        await self._broker.send_aos_focus_clear()

    # ------------------------------------------------------------------
    # State — from AOS.AOSPubDataSV.AOSDataPacket (~1 Hz)
    # ------------------------------------------------------------------

    @property
    def total_offset(self) -> float | None:
        """Current total focus offset in meters, or None if not yet received."""
        if aos := self._broker.store.aos:
            return aos.totalFocusOffset
        return None

    @property
    def out_of_range(self) -> bool | None:
        """True if the focus offset demand is out of range."""
        if aos := self._broker.store.aos:
            return aos.focusOffsetDemandOutOfRange
        return None

    @property
    def detailed_state(self) -> str | None:
        """AOS detailed state string (e.g. ``"ClosedLoopState"``)."""
        if aos := self._broker.store.aos:
            return aos.detailedState
        return None

    @property
    def m1f_settled(self) -> bool | None:
        """M1 actuator force loop settled."""
        if aos := self._broker.store.aos:
            return aos.M1FSettled
        return None

    @property
    def m1l_settled(self) -> bool | None:
        """M1 lateral control settled."""
        if aos := self._broker.store.aos:
            return aos.M1LSettled
        return None

    @property
    def m1p_settled(self) -> bool | None:
        """M1 actuator position loop settled."""
        if aos := self._broker.store.aos:
            return aos.M1PSettled
        return None

    @property
    def m2p_settled(self) -> bool | None:
        """M2 actuator position loop settled."""
        if aos := self._broker.store.aos:
            return aos.M2PSettled
        return None

    @property
    def m2v_settled(self) -> bool | None:
        """M2 vacuum system settled."""
        if aos := self._broker.store.aos:
            return aos.M2VSettled
        return None
