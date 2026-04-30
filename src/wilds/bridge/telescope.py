"""
Telescope — high-level async facade for TCS commands and state.

Wraps LDTBroker to provide a clean interface for offset commands and
reading current telescope state from TelemetryStore.

Usage::

    telescope = Telescope(broker)

    await telescope.offset(-8.1, 12.0)
    await telescope.clear_offset()

    if telescope.in_position:
        print(telescope.par_angle)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models.tcs_command import TcsAbsorbOffsetCommand, TcsClearOffsetCommand, TcsOffsetCommand
from .models.tcs_status import _PointingPositions
from .models.types import CoordFrame, OffsetNum, OffsetType, TcsHealth, TcsState

if TYPE_CHECKING:
    from .broker import LDTBroker


class Telescope:
    """
    Async facade for telescope control and state.

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

    async def offset(
        self,
        ra: float,
        dec: float,
        *,
        offset_type: OffsetType = "TPLANE",
        num: OffsetNum = "User",
    ) -> None:
        """Apply a science-target offset.

        Parameters
        ----------
        ra:
            RA (or Az) component in arcsec.
        dec:
            Dec (or El) component in arcsec.
        offset_type:
            ``"TPLANE"`` (tangent-plane, arcsec) or ``"SIMPLE"``
            (RA in seconds of time, Dec in arcsec).
        num:
            ``"User"`` for dither-grid offsets; ``"Handset"`` for
            acquisition tweaks.  Default ``"User"``.
        """
        cmd = TcsOffsetCommand.make_offset(ra, dec, offset_type=offset_type, num1=num)
        await self._broker.send_tcs_command(cmd)

    async def clear_offset(self, *, num: OffsetNum = "User") -> None:
        """Set RA/Dec offsets back to 0, 0."""
        await self._broker.send_tcs_command(TcsClearOffsetCommand.make(num2=num))

    async def absorb_offset(self, *, num: OffsetNum = "User") -> None:
        """Bake the current offset into the target coordinates and clear it."""
        await self._broker.send_tcs_command(TcsAbsorbOffsetCommand.make(num2=num))

    # ------------------------------------------------------------------
    # State — from tcs.loisTelemetry (~2 Hz)
    # ------------------------------------------------------------------

    @property
    def in_position(self) -> bool | None:
        if tcs := self._broker.store.tcs:
            return tcs.InPosition
        return None

    @property
    def par_angle(self) -> float | None:
        if tcs := self._broker.store.tcs:
            if tcs.CurrentParAngle is not None:
                return float(tcs.CurrentParAngle)
        return None

    @property
    def tcs_health(self) -> TcsHealth | None:
        if tcs := self._broker.store.tcs:
            return tcs.TCSHealth
        return None

    @property
    def tcs_state(self) -> TcsState | None:
        if tcs := self._broker.store.tcs:
            return tcs.TCSState
        return None

    @property
    def target_frame(self) -> CoordFrame | None:
        if tcs := self._broker.store.tcs:
            return tcs.TargetFrame
        return None

    # ------------------------------------------------------------------
    # State — from TCSTcsStatusSV (~1 Hz)
    # ------------------------------------------------------------------

    @property
    def pointing(self) -> _PointingPositions | None:
        """Full pointing block from TcsStatus, or None if not yet received."""
        if status := self._broker.store.tcs_status:
            return status.pointingPositions
        return None
