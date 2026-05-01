"""
pydantic-xml models for TCS commands.

Offset commands publish to:
  TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV
  (reply on TCSTcsCommandResponseSV)

New-target command publishes to:
  TCS.TCSSharedVariables.TCSLowLevelStatusSV.NewScienceTargetSV

commandID per LIG spec: microseconds since midnight UT.
  round((now.hour*3600 + now.minute*60 + now.second + now.microsecond/1e6) * 1e6)

Offset command types (root tag varies):
  <scienceTargetOffset>        — apply RA/Dec or Az/El offset (arcsec)
  <scienceTargetClearOffset>   — set offsets back to 0, 0
  <scienceTargetAbsorbOffset>  — bake offset into target coords and clear

offsetType: "TPLANE" (tangent plane, arcsec) or "SIMPLE" (RA in seconds, Dec in arcsec)
num1/num2:  "User" (dither grid) or "Handset" (acquisition tweaks)
"""

import datetime
from typing import Literal

from pydantic_xml import BaseXmlModel, attr, element

from .types import CoordFrame, EquinoxPrefix, OffsetNum, OffsetType, RotatorFrame


def _make_command_id() -> int:
    now = datetime.datetime.now(datetime.UTC)
    return round(
        (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) * 1e6
    )


class _TcsErrorResponse(BaseXmlModel):
    """Placeholder sent with commands; TCS fills it in on the reply."""

    code: int = element(default=0)
    source: str | None = element(default=None)
    status: bool = element(default=False)


class _OffsetDef(BaseXmlModel):
    num1: OffsetNum = element(default="User")
    off1: float = element()                                        # RA or Az component, arcsec
    off2: float = element()                                        # Dec or El component, arcsec
    offsetType: OffsetType = element(default="TPLANE")


class TcsOffsetCommand(BaseXmlModel, tag="scienceTargetOffset"):
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    offsetDef: _OffsetDef = element()

    @classmethod
    def make_offset(
        cls,
        off1: float,
        off2: float,
        offset_type: OffsetType = "TPLANE",
        num1: OffsetNum = "User",
    ) -> "TcsOffsetCommand":
        return cls(
            commandID=_make_command_id(),
            offsetDef=_OffsetDef(off1=off1, off2=off2, offsetType=offset_type, num1=num1),
        )


class TcsClearOffsetCommand(BaseXmlModel, tag="scienceTargetClearOffset"):
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    num2: OffsetNum = element(default="User")

    @classmethod
    def make(cls, num2: OffsetNum = "User") -> "TcsClearOffsetCommand":
        return cls(commandID=_make_command_id(), num2=num2)


class TcsAbsorbOffsetCommand(BaseXmlModel, tag="scienceTargetAbsorbOffset"):
    """Bakes the current offset into the target coordinates and clears it."""

    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    num2: OffsetNum = element(default="User")

    @classmethod
    def make(cls, num2: OffsetNum = "User") -> "TcsAbsorbOffsetCommand":
        return cls(commandID=_make_command_id(), num2=num2)


# ---------------------------------------------------------------------------
# New science target — NewScienceTargetSV
# ---------------------------------------------------------------------------


class _Dec(BaseXmlModel):
    degreesDec: float = element()
    minutesArc: int = element()
    secondsArc: float = element()


class _RA(BaseXmlModel):
    hours: float = element()
    minutesTime: int = element()
    secondsTime: float = element()


class _TargetRADec(BaseXmlModel):
    """Element order matches the XML schema: declination, equinox, frame, ra."""

    declination: _Dec = element()
    equinoxPrefix: EquinoxPrefix = element()
    equinoxYear: float = element()
    frame: CoordFrame = element()
    ra: _RA = element()


class _NewTargetRotator(BaseXmlModel):
    rotPA: float = element()
    rotatorFrame: RotatorFrame = element()


class _ProperMotion(BaseXmlModel):
    epochPM_Yr: float = element()
    pmRA_masPYr: float = element()
    pmDec_masPYr: float = element()


class _Difftrack(BaseXmlModel):
    class_: str = attr(
        name="class",
        default="TCSDataDefinitions.TCSCommand.TargetConfiguration.Target.DifftrackRADec",
    )
    dRA_ArcsPS: float = element()
    dDec_ArcsPS: float = element()


class _FixedTarget(BaseXmlModel):
    class_: str = attr(
        name="class",
        default="TCSDataDefinitions.TCSCommand.TargetConfiguration.Target.FixedTarget.RADecTarget",
    )
    raDecParameters: _TargetRADec = element()
    parallax_Arcsec: float = element()
    properMotion: _ProperMotion = element()
    rv_kps: float = element()
    targetName: str = element()
    difftrack: _Difftrack = element()


class _ScienceTargetConfig(BaseXmlModel):
    fracrate: float = element()
    rotator: _NewTargetRotator = element()
    target: _FixedTarget = element()
    targetConfigName: str = element()
    wl_microns: float = element()
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)


class TcsNewScienceTargetCommand(BaseXmlModel, tag="newScienceTarget"):
    """
    Command a new science target slew.

    Publish to: TCS.TCSSharedVariables.TCSLowLevelStatusSV.NewScienceTargetSV

    Depending on the TCS operator state, the telescope will either queue
    the target for preview or begin slewing immediately.
    """

    demandRADec: _TargetRADec = element()
    pointingOriginX: float = element(default=0.0)
    pointingOriginY: float = element(default=0.0)
    scienceTargetConfiguration: _ScienceTargetConfig = element()
    trackID: float = element(default=0.0)

    @classmethod
    def make(
        cls,
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
    ) -> "TcsNewScienceTargetCommand":
        radec = _TargetRADec(
            declination=_Dec(degreesDec=dec_deg, minutesArc=0, secondsArc=0.0),
            equinoxPrefix=equinox_prefix,
            equinoxYear=equinox_year,
            frame=frame,
            ra=_RA(hours=ra_hours, minutesTime=0, secondsTime=0.0),
        )
        return cls(
            demandRADec=radec,
            scienceTargetConfiguration=_ScienceTargetConfig(
                fracrate=1.0,
                rotator=_NewTargetRotator(rotPA=rot_pa, rotatorFrame=rot_frame),
                target=_FixedTarget(
                    raDecParameters=radec,
                    parallax_Arcsec=parallax_arcsec,
                    properMotion=_ProperMotion(
                        epochPM_Yr=equinox_year,
                        pmRA_masPYr=pm_ra_maspyr,
                        pmDec_masPYr=pm_dec_maspyr,
                    ),
                    rv_kps=rv_kps,
                    targetName=target_name,
                    difftrack=_Difftrack(dRA_ArcsPS=0.0, dDec_ArcsPS=0.0),
                ),
                targetConfigName=target_name,
                wl_microns=wl_microns,
                commandID=_make_command_id(),
            ),
        )
