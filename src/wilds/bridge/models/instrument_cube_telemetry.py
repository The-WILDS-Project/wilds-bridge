"""
pydantic-xml model for:
  instrumentCube.loisTelemetry

Published by JOE at ~1 Hz.
Reports fold-mirror (FMA–FMD) positions and instrument cover state.
Relevant for FITS headers to record which instrument port is in use.

Schema reference:
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/instrumentCube.loisTelemetry.xsd
"""

from typing import Literal

from pydantic_xml import BaseXmlModel, element

from .types import FoldMirrorState


class InstrumentCubeTelemetry(BaseXmlModel, tag="InstrumentCubeTelemetry"):
    """Field order matches XSD element order."""

    TimeStamp: int | None = element(default=None)
    InstrumentCoverState: Literal["Unknown", "Open", "Closed"] | None = element(default=None)
    InstrumentCoverPosition: float | None = element(default=None)      # mm
    FMAState: FoldMirrorState | None = element(default=None)
    FMAPosition: float | None = element(default=None)                  # mm
    FMBState: FoldMirrorState | None = element(default=None)
    FMBPosition: float | None = element(default=None)
    FMCState: FoldMirrorState | None = element(default=None)
    FMCPosition: float | None = element(default=None)
    FMDState: FoldMirrorState | None = element(default=None)
    FMDPosition: float | None = element(default=None)
