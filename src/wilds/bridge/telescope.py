"""
Telescope — high-level async facade for TCS commands and state.

Wraps LDTBroker to provide a clean interface for offset commands and
reading current telescope state from TelemetryStore.

Usage::

    telescope = Telescope(broker)

    await telescope.offset(-8.1, 12.0)
    await telescope.clear_offset()
    await telescope.set_rotator(45.0)       # slit sky PA, keeping the current target

    if telescope.in_position:
        print(telescope.par_angle)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .models.tcs_command import (
    TcsAbsorbOffsetCommand,
    TcsClearOffsetCommand,
    TcsOffsetCommand,
    TcsScienceTargetCommand,
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


class TargetUnknownError(RuntimeError):
    """The TCS's current target isn't known, so it can't be re-sent safely."""


class TelescopeStatus(BaseModel):
    """Snapshot of telescope state from both telemetry sources."""

    model_config = ConfigDict(frozen=True)

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
        rot_frame: RotatorFrame = "Target",
        wl_microns: float = 0.5,
        pm_ra_maspyr: float = 0.0,
        pm_dec_maspyr: float = 0.0,
        parallax_arcsec: float = 0.0,
        rv_kps: float = 0.0,
    ) -> None:
        """Command a new science target slew.

        Sends a ``<scienceTargetConfiguration>`` to TCSTcsCommandSV. With the TCS's
        External Command Preview on, the operator must approve it before the slew.

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
            Instrument position angle in degrees (0–360, East of North): the sky PA of
            the instrument principal direction, i.e. the slit.
        rot_frame:
            ``"Target"`` (TCS default): the rotator tracks in the target's frame, so the
            field holds still on the slit at ``rot_pa``. ``"Fixed"``: the TCS ignores the
            IAA, adds 180° to ``rot_pa`` and tracks in Az/El, holding the mechanical
            rotator near that angle while the sky rotates past.
            See TCS External Interface Definitions (DCT-0720S-005-I) §3.3.3.2.
        wl_microns:
            Guide wavelength in microns for atmospheric dispersion (default 0.5).
        pm_ra_maspyr / pm_dec_maspyr:
            Proper motion in mas/yr.
        parallax_arcsec:
            Parallax in arcsec.
        rv_kps:
            Radial velocity in km/s.
        """
        cmd = TcsScienceTargetCommand.make(
            target_name, ra_hours, dec_deg,
            frame=frame, equinox_prefix=equinox_prefix, equinox_year=equinox_year,
            rot_pa=rot_pa, rot_frame=rot_frame, wl_microns=wl_microns,
            pm_ra_maspyr=pm_ra_maspyr, pm_dec_maspyr=pm_dec_maspyr,
            parallax_arcsec=parallax_arcsec, rv_kps=rv_kps,
        )
        await self._broker.send_tcs_command(cmd)

    async def set_rotator(self, rot_pa: float, *, rot_frame: RotatorFrame | None = None) -> None:
        """Rotate the slit to a new sky PA, keeping the current target.

        The TCS has no rotator-only command. As LDT's own software does it (Tim
        Ellsworth-Bowers, 2026-11-02), this takes the TCS's latest report of its current
        target (NewScienceTargetSV), replaces only the rotator and sends the result to
        TCSTcsCommandSV, so offsets and differential tracking rates are preserved.

        Parameters
        ----------
        rot_pa:
            Slit sky PA in degrees, East of North; normalised to [0, 360).
        rot_frame:
            ``"Target"`` or ``"Fixed"`` (see :meth:`slew_to`); ``None`` keeps the
            current frame.

        Raises
        ------
        TargetUnknownError
            No target report has been received since the bridge connected, or it names
            a different target than TCSTcsStatusSV, i.e. it may be stale. Re-sending it
            would move the telescope, so nothing is sent.
        """
        report = self._broker.store.new_science_target
        if report is None:
            raise TargetUnknownError(
                "no NewScienceTargetSV report received yet; send a target with slew_to first"
            )
        current = report.scienceTargetConfiguration
        status = self._broker.store.tcs_status
        if status and status.pointingPositions and (name := status.pointingPositions.targetName):
            if name.strip() != current.target.targetName.strip():
                raise TargetUnknownError(
                    f"target report is for {current.target.targetName!r} "
                    f"but the TCS is on {name!r}"
                )
        await self._broker.send_tcs_command(current.with_rotator(rot_pa, rot_frame))

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
            return tcs.CurrentParAngle
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
            par_angle=tcs.CurrentParAngle if tcs else None,
            lst=tcs.TCSLST if tcs else None,
            pointing=pointing,
            airmass=airmass,
            time_to_rot_limit_min=time_to_rot_limit_min,
            time_to_az_limit_min=time_to_az_limit_min,
            offsets=offsets,
        )
