"""
pydantic-xml model for:
  TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV

Published by LabVIEW TCS at ~1 Hz.
Use this topic when you need offset/differential rate information,
or when you need the structured sub-elements rather than the
sexagesimal strings in tcs.loisTelemetry.

Schema reference (v1.8):
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/
  TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV.v1_8.xsd

Only fields relevant to WILDS (FITS headers, ADC control) are modelled.
The full message has many more sub-elements; extend as needed.
"""


from pydantic_xml import BaseXmlModel, element, wrapped


class _SexAngle(BaseXmlModel):
    """Generic sexagesimal angle sub-element (degrees/hours, minutes, seconds)."""
    degreesArc: int | None = element(default=None)
    degreesAlt: int | None = element(default=None)   # elevation uses degreesAlt
    hours: int | None = element(default=None)        # RA uses hours
    minutesArc: int | None = element(default=None)
    minutesTime: int | None = element(default=None)
    secondsArc: float | None = element(default=None)
    secondsTime: float | None = element(default=None)


class _RADec(BaseXmlModel):
    ra: _SexAngle = element()
    declination: _SexAngle = element()
    equinoxPrefix: str | None = element(default=None)
    equinoxYear: float | None = element(default=None)
    targetName: str | None = element(default=None)


class _AzEl(BaseXmlModel):
    azimuth: _SexAngle = element()
    elevation: _SexAngle = element()


class _PointingPositions(BaseXmlModel):
    currentRADec: _RADec = element()
    currentAzEl: _AzEl = element()
    currentParAngle: float | None = element(default=None)


class _CurrentTimes(BaseXmlModel):
    utcTime: str | None = element(default=None)
    lstTime: str | None = element(default=None)


class _Limits(BaseXmlModel):
    airmass: float | None = element(default=None)
    moonProximity: float | None = element(default=None)


class TcsStatus(BaseXmlModel, tag="tcsTCSStatus"):
    tcsVersion: str | None = element(default=None)
    accessMode: str | None = element(default=None)

    heartbeat: int | None = element(default=None)
    inPositionIsTrue: bool | None = element(default=None)

    m1CoverState: str | None = element(default=None)
    mountGuideMode: str | None = element(default=None)   # NoTrack | OpenLoop | ClosedLoop

    tcsHealth: str | None = element(default=None)        # GOOD | WARNING | BAD
    tcsState: str | None = element(default=None)         # STANDBY | OFF | ENABLED | ...

    pointingPositions: _PointingPositions | None = element(default=None)
    currentTimes: _CurrentTimes | None = element(default=None)
    limits: _Limits | None = element(default=None)
