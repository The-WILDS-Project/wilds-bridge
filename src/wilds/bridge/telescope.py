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

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models.tcs_command import (
    TcsAbsorbOffsetCommand,
    TcsClearOffsetCommand,
    TcsNewScienceTargetCommand,
    TcsOffsetCommand,
)
from .models.tcs_status import _OffsetStatus, _PointingPositions
from .models.types import (
    CoordFrame,
    CoverState,
    EquinoxPrefix,
    OffsetNum,
    OffsetType,
    RotatorFrame,
    TcsHealth,
    TcsState,
)

if TYPE_CHECKING:
    from .broker import LDTBroker


@dataclass(frozen=True)
class TelescopeStatus:
    """Snapshot of telescope state from both telemetry sources."""

    # From tcs.loisTelemetry (~2 Hz)
    target_name: str | None
    in_position: bool | None
    tcs_health: TcsHealth | None
    tcs_state: TcsState | None
    guide_mode: str | None
    m1_cover: CoverState | None
    dome_occultation_warning: bool | None
    par_angle: float | None             # degrees
    lst: str | None                     # e.g. "04:41:18.100"

    # From TCSTcsStatusSV (~1 Hz)
    pointing: _PointingPositions | None
    airmass: float | None
    time_to_rot_limit_min: float | None
    time_to_az_limit_min: float | None
    offsets: _OffsetStatus | None


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

    async def slew_to(
        self,
        target_name: str,
        ra_hours: float,
        dec_deg: float,
        *,
        frame: CoordFrame = "FK5",
        equinox_prefix: EquinoxPrefix = "J",
        equinox_year: float = 2000.0,
        rot_pa: float = 0.0,
        rot_frame: RotatorFrame = "Fixed",
        wl_microns: float = 0.5,
        pm_ra_maspyr: float = 0.0,
        pm_dec_maspyr: float = 0.0,
        parallax_arcsec: float = 0.0,
        rv_kps: float = 0.0,
    ) -> None:
        """Command a new science target slew.

        Parameters
        ----------
        target_name:
            Object name sent to the TCS.
        ra_hours:
            Right ascension in decimal hours.
        dec_deg:
            Declination in decimal degrees (signed).
        frame:
            Coordinate frame (default ``"FK5"``).
        equinox_prefix / equinox_year:
            Equinox, e.g. ``"J"`` / ``2000.0``.
        rot_pa:
            Rotator position angle in degrees.
        rot_frame:
            ``"Fixed"`` (sky PA) or ``"Target"`` (parallactic).
        wl_microns:
            Guide wavelength in microns for atmospheric dispersion (default 0.5).
        pm_ra_maspyr / pm_dec_maspyr:
            Proper motion in mas/yr.
        parallax_arcsec:
            Parallax in arcsec.
        rv_kps:
            Radial velocity in km/s.
        """
        cmd = TcsNewScienceTargetCommand.make(
            target_name, ra_hours, dec_deg,
            frame=frame, equinox_prefix=equinox_prefix, equinox_year=equinox_year,
            rot_pa=rot_pa, rot_frame=rot_frame, wl_microns=wl_microns,
            pm_ra_maspyr=pm_ra_maspyr, pm_dec_maspyr=pm_dec_maspyr,
            parallax_arcsec=parallax_arcsec, rv_kps=rv_kps,
        )
        await self._broker.send_new_target(cmd)

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

    # ------------------------------------------------------------------
    # Integrated status snapshot
    # ------------------------------------------------------------------

    @property
    def status(self) -> TelescopeStatus:
        """Frozen snapshot combining both telemetry sources."""
        tcs = self._broker.store.tcs
        tcs_status = self._broker.store.tcs_status

        par_angle = None
        if tcs and tcs.CurrentParAngle is not None:
            par_angle = float(tcs.CurrentParAngle)

        pointing = None
        offsets = None
        airmass = None
        time_to_rot_limit_min = None
        time_to_az_limit_min = None
        if tcs_status:
            pointing = tcs_status.pointingPositions
            offsets = tcs_status.offsetStatus
            if limits := tcs_status.limits:
                airmass = limits.airmass
                time_to_rot_limit_min = limits.timeToRotLimit_min
                time_to_az_limit_min = limits.timeToAzLimit_min

        return TelescopeStatus(
            target_name=tcs.ScienceTargetName if tcs else None,
            in_position=tcs.InPosition if tcs else None,
            tcs_health=tcs.TCSHealth if tcs else None,
            tcs_state=tcs.TCSState if tcs else None,
            guide_mode=tcs.MountGuideMode if tcs else None,
            m1_cover=tcs.m1CoverState if tcs else None,
            dome_occultation_warning=tcs.DomeOccultationWarning if tcs else None,
            par_angle=par_angle,
            lst=tcs.TCSLST if tcs else None,
            pointing=pointing,
            airmass=airmass,
            time_to_rot_limit_min=time_to_rot_limit_min,
            time_to_az_limit_min=time_to_az_limit_min,
            offsets=offsets,
        )
