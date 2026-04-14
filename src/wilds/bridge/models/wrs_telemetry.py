"""
pydantic-xml model for the wrs.loisTelemetry ActiveMQ topic.

Published by JOE (WRSTelemetry.java) at ~1 Hz.
Contains weather and environmental data used in FITS headers.

Schema reference:
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/wrs.loisTelemetry.xsd
"""


from pydantic_xml import BaseXmlModel, element


class WrsTelemetry(BaseXmlModel, tag="wrsTelemetry"):
    Timestamp: int = element()

    AirTemp: float | None = element(default=None)            # °C
    BarometricPressure: float | None = element(default=None) # mbar
    DewPoint: float | None = element(default=None)           # °C
    RelativeHumidity: float | None = element(default=None)   # %
    WindDirection: float | None = element(default=None)      # degrees
    WindSpeed: float | None = element(default=None)          # m/s
