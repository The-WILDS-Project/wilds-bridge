"""
pydantic-xml model for the tcs.loisTelemetry ActiveMQ topic.

Published by JOE (FacilitySummary.java) at ~2 Hz.
Coordinates (RA, Dec, HA, LST) are sexagesimal strings; angles are decimal degrees.

Known JOE bugs:
  - The same message is sent twice approximately once per minute.
    Deduplication is handled in LDTBroker, not here.
  - At the very start of a night decimal fields may contain "UNKNOWN".
    InboundXmlModel maps these to None.

Schema: schemas/tcs.loisTelemetry.xsd (vendored from ligmos)
"""

import datetime

from pydantic_xml import element

from .inbound import InboundXmlModel
from .types import CoordFrame, CoverState, TcsHealth, TcsState
from .types import RotatorFrame as RotFrame


class TcsTelemetry(InboundXmlModel, tag="TCSTelemetry"):
    # Field order matches XSD element order for correct pydantic-xml parsing.
    # All fields are minOccurs="0" in the schema.

    TimeStamp: int | None = element(default=None)                   # Unix epoch seconds
    TCSLST: str | None = element(default=None)                      # e.g. "04:41:18.100"
    TCSUTC: datetime.datetime | None = element(default=None)
    DemandRa: str | None = element(default=None)                    # sexagesimal
    DemandDec: str | None = element(default=None)                   # sexagesimal
    CurrentHourAngle: str | None = element(default=None)            # e.g. "00:00:07"
    TCSCurrentZenithDistance: float | None = element(default=None)  # degrees
    TCSCurrentAzimuth: float | None = element(default=None)         # degrees
    TCSCurrentElev: float | None = element(default=None)            # degrees
    MountGuideMode: str | None = element(default=None)              # NoTrack | ClosedLoop | ...
    ScienceTargetName: str | None = element(default=None)
    m1CoverState: CoverState | None = element(default=None)
    MountDomeAzimuthDifference: float | None = element(default=None)  # degrees
    DomeOccultationWarning: bool | None = element(default=None)
    CurrentParAngle: float | None = element(default=None)           # degrees
    TCSCurrentRotatorPA: float | None = element(default=None)       # degrees
    TCSCurrentRotatorIAA: float | None = element(default=None)      # degrees
    TCSCurrentRotatorIPA: float | None = element(default=None)      # degrees
    RotatorFrame: RotFrame | None = element(default=None)
    TargetFrame: CoordFrame | None = element(default=None)
    equinox: float | None = element(default=None)                   # e.g. 2000.0
    TCSState: TcsState | None = element(default=None)
    TCSHealth: TcsHealth | None = element(default=None)
    TCSHeartBeat: int | None = element(default=None)
    TCSAccessMode: str | None = element(default=None)               # Operator | Engineer | ...
    InPosition: bool | None = element(default=None)
    MountTemperature: float | None = element(default=None)          # °C
    CLSLowBankState: str | None = element(default=None)             # e.g. "UNKNOWN"
    DSSPositionStatus: str | None = element(default=None)           # e.g. "UNKNOWN"
