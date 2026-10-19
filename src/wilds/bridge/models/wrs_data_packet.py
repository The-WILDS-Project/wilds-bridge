"""
pydantic-xml model for:
  WRS.WRSPubDataSV.WRSDataPacket

Published by the Weather and Ranging System at ~1 Hz when telescope is operational.
All values are metric; barometric pressure is corrected to sea level.
Preferred source for FITS header weather keywords.

Schema: schemas/WRS.WRSPubDataSV.WRSDataPacket.xsd (vendored from ligmos)
"""

import datetime

from pydantic_xml import element

from .inbound import InboundXmlModel


class _WrsStatistics(InboundXmlModel):
    max: float | None = element(default=None)
    min: float | None = element(default=None)
    mean: float | None = element(default=None)


class WrsDataPacket(InboundXmlModel, tag="WRSDataPacket"):
    """Field order matches XSD element order."""

    airTemp_C: float | None = element(default=None)              # °C
    barPressure_mbar: float | None = element(default=None)       # mbar, sea-level corrected
    dewPointCurrentValue: float | None = element(default=None)   # °C
    rainRate: float | None = element(default=None)
    relativeHumidity: float | None = element(default=None)       # %
    timestamp: datetime.datetime | None = element(default=None)
    temperatureStatistics: _WrsStatistics | None = element(default=None)
    tempRateOfChange_C: float | None = element(default=None)     # °C/interval
    windDirection_deg: float | None = element(default=None)      # degrees
    windSpeed: float | None = element(default=None)              # m/s
    tenMinWindGustSpeed: float | None = element(default=None)    # m/s
    windSpeedStatistics: _WrsStatistics | None = element(default=None)
