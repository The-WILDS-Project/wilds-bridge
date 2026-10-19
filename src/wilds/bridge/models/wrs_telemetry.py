"""
pydantic-xml model for the wrs.loisTelemetry ActiveMQ topic.

Published by JOE (WRSTelemetry.java) at ~1 Hz.
Contains weather and environmental data used in FITS headers.

No XSD exists upstream; structure follows schemas/xmlsamples/wrs.loisTelemetry.xml.
"""

from pydantic_xml import element

from .inbound import InboundXmlModel


class WrsTelemetry(InboundXmlModel, tag="WRSTelemetry"):
    TimeStamp: int | None = element(default=None)  # Unix epoch seconds

    AirTemp: float | None = element(default=None)  # °C
    BarometricPressure: float | None = element(default=None)  # mbar
    DewPoint: float | None = element(default=None)  # °C
    RelativeHumidity: float | None = element(default=None)  # %
    WindDirection: float | None = element(default=None)  # degrees
    WindSpeed: float | None = element(default=None)  # m/s
