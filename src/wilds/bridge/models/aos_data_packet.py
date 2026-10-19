"""
pydantic-xml model for:
  AOS.AOSPubDataSV.AOSDataPacket

Published by the AOS (Active Optics System) LabVIEW at ~1 Hz.
Key field for focuser: totalFocusOffset (meters).

Schema: schemas/AOS.AOSPubDataSV.AOSDataPacket.xsd (vendored from ligmos)
"""

import datetime

from pydantic_xml import element

from .inbound import InboundXmlModel


class _TipTiltPiston(InboundXmlModel):
    X_Tilt_rad: float | None = element(default=None)
    Y_Tilt_rad: float | None = element(default=None)
    Piston_m: float | None = element(default=None)


class _ComaPointingOffset(InboundXmlModel):
    xCorrection_arcsec: float | None = element(default=None)
    yCorrection_arcsec: float | None = element(default=None)


class AosDataPacket(InboundXmlModel, tag="AOSDataPacket"):
    """Field order matches XSD element order."""

    timestamp: datetime.datetime | None = element(default=None)
    detailedState: str | None = element(default=None)    # e.g. ClosedLoopState, FaultState
    summaryState: str | None = element(default=None)     # Enabled | OffState | StandbyState | DisabledState | FaultState (inconsistent in docs)
    tipTiltPistonDemandM1: _TipTiltPiston | None = element(default=None)
    tipTiltPistonDemandM2: _TipTiltPiston | None = element(default=None)
    comaPointingOffset: _ComaPointingOffset | None = element(default=None)
    totalFocusOffset: float | None = element(default=None)              # meters; primary focus readback
    focusOffsetDemandOutOfRange: bool | None = element(default=None)
    wavefrontDataOutOfRange: bool | None = element(default=None)
    M1FSettled: bool | None = element(default=None)   # M1 actuator force loop
    M1LSettled: bool | None = element(default=None)   # M1 lateral control
    M1PSettled: bool | None = element(default=None)   # M1 actuator position loop
    M2PSettled: bool | None = element(default=None)   # M2 actuator position loop
    M2VSettled: bool | None = element(default=None)   # M2 vacuum system
