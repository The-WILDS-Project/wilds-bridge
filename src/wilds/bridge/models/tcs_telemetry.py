"""
pydantic-xml model for the tcs.loisTelemetry ActiveMQ topic.

Published by JOE (FacilitySummary.java) at ~2 Hz.
All coordinate values are strings/sexagesimal for easy reading.

Known JOE bugs:
  - The same message is sent twice approximately once per minute.
    Deduplication is handled in LDTBroker, not here.
  - At the very start of a night some float fields may contain "UNKNOWN".
    Fields that can be affected are typed str | None where this is known.

Schema reference:
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/tcs.loisTelemetry.xsd
"""

from pydantic_xml import BaseXmlModel, element


class TcsTelemetry(BaseXmlModel, tag="tcsTelemetry"):
    # Unix epoch seconds
    Timestamp: int = element()

    # Local Sidereal Time  e.g. "04:41:18.100"
    TCSLST: str = element()

    # UTC datetime string  e.g. "2019-12-08T06:59:59.893Z"
    TCSUTC: str = element()

    # RA/Dec demand (sexagesimal strings)
    DemandRa: str = element()
    DemandDec: str = element()

    # Hour angle  e.g. "00:00:07"
    CurrentHourAngle: str = element()

    # Zenith distance, azimuth, elevation (degrees as floats-in-strings)
    TCSCurrentZenithDistance: str = element()
    TCSCurrentAzimuth: str = element()
    TCSCurrentElev: str = element()

    # Rotator angles (degrees as floats-in-strings)
    TCSCurrentRotatorPA: str = element()
    TCSCurrentRotatorIPA: str = element()
    TCSCurrentRotatorIAA: str = element()

    # "Target" or "Fixed"
    RotatorFrame: str = element()

    # "FK4", "FK5", "APPT", "GAPPT", "AZEL"
    TargetFrame: str = element()

    # Equinox year  e.g. "2000.0"
    equinox: str = element()

    # TCS state machine
    TCSState: str = element()       # STANDBY | OFF | ENABLED | DISABLED | FAULT
    TCSHealth: str = element()      # GOOD | WARNING | BAD
    TCSHeartBeat: int = element()   # 1 Hz counter from TCS startup
    TCSAccessMode: str = element()  # Operator | Engineer | ...

    # Pointing
    InPosition: bool = element()
    ScienceTargetName: str = element()

    # Parallactic angle (degrees as float-in-string)
    CurrentParAngle: str = element()

    # Mount temperature (°C)  — can be "UNKNOWN" at startup
    MountTemperature: str | None = element(default=None)

    # Mirror cover
    m1CoverState: str = element()   # Open | Closed | PartiallyOpen | Unknown

    # Dome
    MountDomeAzimuthDifference: str | None = element(default=None)
    DomeOccultationWarning: bool = element()

    # Flat field lamp power supply state
    CLSLowBankState: str | None = element(default=None)

    # Dome shutter
    DSSPositionStatus: str | None = element(default=None)
