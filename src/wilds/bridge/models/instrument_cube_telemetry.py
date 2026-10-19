"""
pydantic-xml model for:
  instrumentCube.loisTelemetry

Published by JOE at ~1 Hz.
Reports fold-mirror (FMA–FMD) positions and instrument cover state.
Relevant for FITS headers to record which instrument port is in use.

States are upper case on the wire (e.g. "CLOSED", "HOME") and kept as plain strings.

Schema: schemas/instrumentCube.loisTelemetry.xsd (vendored from ligmos)
"""

from pydantic_xml import element

from .inbound import InboundXmlModel


class InstrumentCubeTelemetry(InboundXmlModel, tag="InstrumentCubeTelemetry"):
    """Field order matches XSD element order."""

    TimeStamp: int | None = element(default=None)
    InstrumentCoverState: str | None = element(default=None)
    InstrumentCoverPosition: float | None = element(default=None)      # mm
    FMAState: str | None = element(default=None)
    FMAPosition: float | None = element(default=None)                  # mm
    FMBState: str | None = element(default=None)
    FMBPosition: float | None = element(default=None)
    FMCState: str | None = element(default=None)
    FMCPosition: float | None = element(default=None)
    FMDState: str | None = element(default=None)
    FMDPosition: float | None = element(default=None)
