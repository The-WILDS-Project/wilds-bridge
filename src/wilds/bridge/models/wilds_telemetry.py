"""
pydantic-xml model for the wilds.loisTelemetry ActiveMQ topic.

This is the WILDS instrument status topic, published by the bridge
to the LDT ActiveMQ broker so LDT infrastructure (LOUI, etc.) can
monitor instrument state — analogous to deveny.loisTelemetry.

Schema to be agreed with LIG (Ryan Hamilton, rhamilton@lowell.edu).
Fields here are a proposed first draft; extend as the instrument design
and LIG discussions progress.
"""

import datetime

from pydantic_xml import BaseXmlModel, element


class WildsTelemetry(BaseXmlModel, tag="wildsTelemetry"):
    # Unix epoch seconds — always present
    Timestamp: int = element()

    # --- Slit ---
    SlitPositionMM: float | None = element(default=None)  # mm
    SlitPositionASEC: float | None = element(default=None)  # arcseconds on sky

    # --- ADC ---
    # Two linear stages; positions in mm from home
    ADC1PositionMM: float | None = element(default=None)
    ADC2PositionMM: float | None = element(default=None)
    # Parallactic angle used for ADC positioning (from tcs.loisTelemetry)
    ADCParAngleDeg: float | None = element(default=None)

    # --- Shutters ---
    # One or more shutters; names TBD pending hardware selection
    Shutter1State: str | None = element(default=None)  # Open | Closed | Unknown

    # --- Detectors ---
    # VIS channel (Archon 1)
    VISExposureState: str | None = element(default=None)  # IDLE | EXPOSING | READING
    VISExposureTime: float | None = element(default=None)
    VISCCDTemp: float | None = element(default=None)  # °C

    # UV channel (Archon 2)
    UVExposureState: str | None = element(default=None)
    UVExposureTime: float | None = element(default=None)
    UVCCDTemp: float | None = element(default=None)  # °C

    # --- Guide camera ---
    GuideCameraState: str | None = element(default=None)

    # --- Software ---
    # Last FITS file written (VIS and UV)
    LastFITSFileVIS: str | None = element(default=None)
    LastFITSFileUV: str | None = element(default=None)

    @classmethod
    def now(cls, **kwargs) -> "WildsTelemetry":
        """Convenience constructor that fills Timestamp with current UTC epoch."""
        return cls(
            Timestamp=int(datetime.datetime.now(datetime.UTC).timestamp()),
            **kwargs,
        )
