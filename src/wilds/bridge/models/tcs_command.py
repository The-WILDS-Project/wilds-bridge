"""
pydantic-xml models for TCS commands.

All commands publish to:
  TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV
  (reply on TCSTcsCommandResponseSV)

A new science target is a <scienceTargetConfiguration> command on that topic
(Tim Ellsworth-Bowers, 2026-11-02). NewScienceTargetSV is TCS → broker: the TCS
reports its current target there, wrapped in <newScienceTarget>; messages
published to it never reach the TCS.

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

from pydantic_xml import BaseXmlModel, attr, element

from .types import CoordFrame, EquinoxPrefix, OffsetNum, OffsetType, RotatorFrame

# Target models also parse the TCS's own reports (NewScienceTargetSV), whose element
# order needn't match ours: LIG's examples order tcsErrorResponse differently for
# offsets and targets. Serialisation still follows field order.
_UNORDERED = "unordered"


def _make_command_id() -> int:
    now = datetime.datetime.now(datetime.UTC)
    return round(
        (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) * 1e6
    )


class _TcsErrorResponse(BaseXmlModel, search_mode=_UNORDERED):
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
# Science target — command on TCSTcsCommandSV, telemetry on NewScienceTargetSV
# ---------------------------------------------------------------------------


class _Dec(BaseXmlModel, search_mode=_UNORDERED):
    degreesDec: float = element()
    minutesArc: int = element()
    secondsArc: float = element()


class _RA(BaseXmlModel, search_mode=_UNORDERED):
    hours: float = element()
    minutesTime: int = element()
    secondsTime: float = element()


class _TargetRADec(BaseXmlModel, search_mode=_UNORDERED):
    """Element order matches the XML schema: declination, equinox, frame, ra."""

    declination: _Dec = element()
    equinoxPrefix: EquinoxPrefix = element()
    equinoxYear: float = element()
    frame: CoordFrame = element()
    ra: _RA = element()


class _NewTargetRotator(BaseXmlModel, search_mode=_UNORDERED):
    rotPA: float = element()
    rotatorFrame: RotatorFrame = element()


class _ProperMotion(BaseXmlModel, search_mode=_UNORDERED):
    epochPM_Yr: float = element()
    pmRA_masPYr: float = element()
    pmDec_masPYr: float = element()


class _Difftrack(BaseXmlModel, search_mode=_UNORDERED):
    class_: str = attr(
        name="class",
        default="TCSDataDefinitions.TCSCommand.TargetConfiguration.Target.DifftrackRADec",
    )
    dRA_ArcsPS: float = element()
    dDec_ArcsPS: float = element()


class _FixedTarget(BaseXmlModel, search_mode=_UNORDERED):
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


class TcsScienceTargetCommand(
    BaseXmlModel, tag="scienceTargetConfiguration", search_mode=_UNORDERED
):
    """
    Command a new science target slew.

    Publish to: TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV

    Depending on the TCS operator state, the telescope will either queue
    the target for preview or begin slewing immediately.

    The rotator is set only through this command (JIRA TCSD-131): to rotate, re-send
    the current target with a new ``rotator``.
    """

    fracrate: float = element()
    rotator: _NewTargetRotator = element()
    target: _FixedTarget = element()
    targetConfigName: str = element()
    wl_microns: float = element()
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)

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
        rot_frame: RotatorFrame = "Target",
        wl_microns: float = 0.5,
        pm_ra_maspyr: float = 0.0,
        pm_dec_maspyr: float = 0.0,
        parallax_arcsec: float = 0.0,
        rv_kps: float = 0.0,
    ) -> "TcsScienceTargetCommand":
        radec = _TargetRADec(
            declination=_Dec(degreesDec=dec_deg, minutesArc=0, secondsArc=0.0),
            equinoxPrefix=equinox_prefix,
            equinoxYear=equinox_year,
            frame=frame,
            ra=_RA(hours=ra_hours, minutesTime=0, secondsTime=0.0),
        )
        return cls(
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
        )

    def with_rotator(
        self, rot_pa: float, rot_frame: RotatorFrame | None = None
    ) -> "TcsScienceTargetCommand":
        """
        The same target with a new rotator, ready to send as a new command.

        Everything else (coordinates, offsets' basis, differential rates, wavelength)
        is kept. ``rot_pa`` is normalised to [0, 360); ``rot_frame=None`` keeps the
        current frame. The copy gets a fresh commandID and a clean tcsErrorResponse.
        """
        rotator = _NewTargetRotator(
            rotPA=rot_pa % 360.0, rotatorFrame=rot_frame or self.rotator.rotatorFrame
        )
        return self.model_copy(
            deep=True,
            update={
                "rotator": rotator,
                "commandID": _make_command_id(),
                "tcsErrorResponse": _TcsErrorResponse(),
            },
        )


class TcsNewScienceTarget(BaseXmlModel, tag="newScienceTarget", search_mode=_UNORDERED):
    """
    The TCS's current science target, as it reports it.

    Published by the TCS on: TCS.TCSSharedVariables.TCSLowLevelStatusSV.NewScienceTargetSV
    (TCS → broker only). ``scienceTargetConfiguration`` is the starting point for
    re-sending the target, e.g. with a new rotator, which keeps any offsets and
    differential rates.
    """

    demandRADec: _TargetRADec = element()
    pointingOriginX: float = element(default=0.0)
    pointingOriginY: float = element(default=0.0)
    scienceTargetConfiguration: TcsScienceTargetCommand = element()
    trackID: float = element(default=0.0)
