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

from .types import LampPosition


class WildsTelemetry(BaseXmlModel, tag="wildsTelemetry"):
    # Unix epoch seconds — always present
    Timestamp: int = element()

    # --- Slit ---
    # Width set by a stage; the spectrograph cameras see the light through the slit
    SlitWidthMM: float | None = element(default=None)  # mm
    SlitWidthASEC: float | None = element(default=None)  # arcseconds on sky

    # --- Calibration lamps ---
    # Two lamps, each switched on/off and moved in/out of the optical path by a stage
    Lamp1Name: str | None = element(default=None)
    Lamp1State: bool | None = element(default=None)  # on/off
    Lamp1Position: LampPosition | None = element(default=None)
    Lamp2Name: str | None = element(default=None)
    Lamp2State: bool | None = element(default=None)
    Lamp2Position: LampPosition | None = element(default=None)

    # --- ADC ---
    # Two linear stages; positions in mm from home
    ADC1PositionMM: float | None = element(default=None)
    ADC2PositionMM: float | None = element(default=None)
    # Parallactic angle used for ADC positioning (from tcs.loisTelemetry)
    ADCParAngleDeg: float | None = element(default=None)

    # --- Shutter ---
    # Single shutter, driven by the Archon
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
    # ZWO ASI294-class camera viewing the sky around the slit via a static mirror
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
