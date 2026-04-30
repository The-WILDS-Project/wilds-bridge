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

from typing import Literal

from pydantic_xml import BaseXmlModel, element

from .types import CoordFrame, CoverState, TcsHealth, TcsState


class TcsTelemetry(BaseXmlModel, tag="TCSTelemetry"):
    # Field order matches XSD element order for correct pydantic-xml parsing.
    # All fields are minOccurs="0" in the schema.

    TimeStamp: int | None = element(default=None)                 # Unix epoch seconds
    TCSLST: str | None = element(default=None)                    # e.g. "04:41:18.100"
    TCSUTC: str | None = element(default=None)                    # e.g. "2019-12-08T06:59:59.893Z"
    DemandRa: str | None = element(default=None)                  # sexagesimal
    DemandDec: str | None = element(default=None)                 # sexagesimal
    CurrentHourAngle: str | None = element(default=None)          # e.g. "00:00:07"
    TCSCurrentZenithDistance: str | None = element(default=None)  # degrees
    TCSCurrentAzimuth: str | None = element(default=None)         # degrees
    TCSCurrentElev: str | None = element(default=None)            # degrees
    MountGuideMode: str | None = element(default=None)            # NoTrack | ClosedLoop | ... (not fully enumerated)
    ScienceTargetName: str | None = element(default=None)
    m1CoverState: CoverState | None = element(default=None)
    MountDomeAzimuthDifference: str | None = element(default=None)  # can be "UNKNOWN" (JOE bug)
    DomeOccultationWarning: bool | None = element(default=None)
    CurrentParAngle: str | None = element(default=None)           # degrees
    TCSCurrentRotatorPA: str | None = element(default=None)       # degrees
    TCSCurrentRotatorIAA: str | None = element(default=None)      # degrees
    TCSCurrentRotatorIPA: str | None = element(default=None)      # degrees
    RotatorFrame: Literal["Target", "Fixed"] | None = element(default=None)
    TargetFrame: CoordFrame | None = element(default=None)
    equinox: str | None = element(default=None)                   # e.g. "2000.0"
    TCSState: TcsState | None = element(default=None)
    TCSHealth: TcsHealth | None = element(default=None)
    TCSHeartBeat: int | None = element(default=None)
    TCSAccessMode: str | None = element(default=None)             # Operator | Engineer | ... (not fully enumerated)
    InPosition: bool | None = element(default=None)
    MountTemperature: str | None = element(default=None)          # °C; can be "UNKNOWN" at startup
    CLSLowBankState: Literal["On", "Off", "Ramping", "Fault", "Unknown"] | None = element(default=None)
    DSSPositionStatus: CoverState | None = element(default=None)
