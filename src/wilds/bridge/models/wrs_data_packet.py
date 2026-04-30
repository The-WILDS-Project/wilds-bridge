"""
pydantic-xml model for:
  WRS.WRSPubDataSV.WRSDataPacket

Published by the Weather and Ranging System at ~1 Hz when telescope is operational.
All values are metric; barometric pressure is corrected to sea level.
Preferred source for FITS header weather keywords.

Schema reference:
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/WRS.WRSPubDataSV.WRSDataPacket.xsd
"""

from pydantic_xml import BaseXmlModel, element


class _WrsStatistics(BaseXmlModel):
    max: float | None = element(default=None)
    min: float | None = element(default=None)
    mean: float | None = element(default=None)


class WrsDataPacket(BaseXmlModel, tag="WRSDataPacket"):
    """Field order matches XSD element order."""

    airTemp_C: float | None = element(default=None)              # °C
    barPressure_mbar: float | None = element(default=None)       # mbar, sea-level corrected
    dewPointCurrentValue: float | None = element(default=None)   # °C
    rainRate: float | None = element(default=None)
    relativeHumidity: float | None = element(default=None)       # %
    timestamp: str | None = element(default=None)                # ISO-8601 with UTC offset
    temperatureStatistics: _WrsStatistics | None = element(default=None)
    tempRateOfChange_C: float | None = element(default=None)     # °C/interval
    windDirection_deg: float | None = element(default=None)      # degrees
    windSpeed: float | None = element(default=None)              # m/s
    tenMinWindGustSpeed: float | None = element(default=None)    # m/s
    windSpeedStatistics: _WrsStatistics | None = element(default=None)
