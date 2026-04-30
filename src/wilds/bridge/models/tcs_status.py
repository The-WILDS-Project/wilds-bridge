"""
pydantic-xml model for:
  TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV

Published by LabVIEW TCS at ~1 Hz.
Schema: V1.9 (observed live from tanagra.lowell.edu 2026-04-29).
Only fields relevant to WILDS are modelled; unknown elements are ignored.
"""

from typing import Literal

from pydantic_xml import BaseXmlModel, element

from .types import CoordFrame, CoverState, OffsetType, TcsHealth, TcsState


class _SexAngle(BaseXmlModel):
    """Sexagesimal angle — present fields vary by context."""

    degreesArc: int | None = element(default=None)    # azimuth degrees
    degreesAlt: int | None = element(default=None)    # elevation degrees
    degreesDec: str | None = element(default=None)    # declination degrees (may be "-0")
    hours: int | None = element(default=None)         # RA / HA / LST hours
    minutesArc: int | None = element(default=None)
    minutesTime: int | None = element(default=None)
    secondsArc: float | None = element(default=None)
    secondsTime: float | None = element(default=None)


class _AzEl(BaseXmlModel):
    azimuth: _SexAngle = element()
    elevation: _SexAngle = element()


class _RADec(BaseXmlModel):
    """V1.9: declination comes before ra; frame added; targetName removed."""

    declination: _SexAngle = element()
    equinoxPrefix: Literal["J", "B"] | None = element(default=None)
    equinoxYear: float | None = element(default=None)
    frame: CoordFrame | None = element(default=None)
    ra: _SexAngle = element()


class _RotatorPositions(BaseXmlModel):
    rotPA: float | None = element(default=None)
    iaa: float | None = element(default=None)
    rotIPA: float | None = element(default=None)


class _AzElError(BaseXmlModel):
    azError: float | None = element(default=None)
    elError: float | None = element(default=None)


class _DifftrackStatus(BaseXmlModel):
    dAz_ArcsPS: float | None = element(default=None)
    dEl_ArcsPS: float | None = element(default=None)
    dRA_ArcsPS: float | None = element(default=None)
    dDec_ArcsPS: float | None = element(default=None)


class _ObjectPA(BaseXmlModel):
    EqPA: float | None = element(default=None)
    AzPA: float | None = element(default=None)


class _DemandRotatorPositions(BaseXmlModel):
    rotPA: float | None = element(default=None)


class _PointingPositions(BaseXmlModel):
    """V1.9 field order matches XML element order for correct parsing."""

    azElError: _AzElError | None = element(default=None)
    currentAzEl: _AzEl = element()
    currentHA: _SexAngle | None = element(default=None)
    currentRADec: _RADec = element()
    currentParAngle: float | None = element(default=None)
    currentRotatorPositions: _RotatorPositions | None = element(default=None)
    difftrackStatus: _DifftrackStatus | None = element(default=None)
    objectPA: _ObjectPA | None = element(default=None)
    demandAzEl: _AzEl | None = element(default=None)
    demandRADec: _RADec | None = element(default=None)
    demandRotatorPositions: _DemandRotatorPositions | None = element(default=None)
    targetName: str | None = element(default=None)


class _Lst(BaseXmlModel):
    hours: int | None = element(default=None)
    minutesTime: int | None = element(default=None)
    secondsTime: float | None = element(default=None)


class _CurrentTimes(BaseXmlModel):
    """V1.9: lst is a sub-element; time is an ISO-8601 UTC string."""

    lst: _Lst | None = element(default=None)
    time: str | None = element(default=None)


class _ProximityAlert(BaseXmlModel):
    distance_deg: float | None = element(default=None)
    proximityFlag: bool | None = element(default=None)


class _Zenith(BaseXmlModel):
    currentZD_deg: float | None = element(default=None)
    elZenithLimit_deg: float | None = element(default=None)
    inBlindSpotIsTrue: bool | None = element(default=None)
    timeToBlindSpot_min: float | None = element(default=None)
    timeToBlindSpotExit_min: float | None = element(default=None)


class _Limits(BaseXmlModel):
    moonProximity: _ProximityAlert | None = element(default=None)
    sunProximity: _ProximityAlert | None = element(default=None)
    zenith: _Zenith | None = element(default=None)
    airmass: float | None = element(default=None)
    currentTimeToObservable_min: float | None = element(default=None)
    currentTimeToUnobservable_min: float | None = element(default=None)
    timeToRotLimit_min: float | None = element(default=None)
    timeToAzLimit_min: float | None = element(default=None)


class _OffsetStatus(BaseXmlModel):
    offsetType: OffsetType | None = element(default=None)
    userOff1: float | None = element(default=None)
    userOff2: float | None = element(default=None)
    handsetOff1: float | None = element(default=None)
    handsetOff2: float | None = element(default=None)


class TcsStatus(BaseXmlModel, tag="tcsTCSStatus"):
    """V1.9 field order matches XML element order for correct parsing."""

    tcsVersion: str | None = element(default=None)
    accessMode: str | None = element(default=None)
    azCurrentWrap: int | None = element(default=None)
    heartbeat: int | None = element(default=None)
    inPositionIsTrue: bool | None = element(default=None)
    m1CoverState: CoverState | None = element(default=None)
    mountGuideMode: str | None = element(default=None)             # not fully enumerated
    rotCurrentWrap: int | None = element(default=None)
    tcsHealth: TcsHealth | None = element(default=None)
    tcsState: TcsState | None = element(default=None)
    currentTimes: _CurrentTimes | None = element(default=None)
    limits: _Limits | None = element(default=None)
    pointingPositions: _PointingPositions | None = element(default=None)
    offsetStatus: _OffsetStatus | None = element(tag="OffsetStatus", default=None)
    axesTrackMode: str | None = element(default=None)
    inPositionAzIsTrue: bool | None = element(default=None)
    inPositionElIsTrue: bool | None = element(default=None)
    inPositionRotIsTrue: bool | None = element(default=None)
