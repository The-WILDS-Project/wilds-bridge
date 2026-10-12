"""
pydantic-xml model for the deveny.loisTelemetry ActiveMQ topic.

Published by JOE at ~1 Hz with the DeVeny spectrograph's instrument state.
WILDS replaces DeVeny at LDT; this model is kept as the reference that
wilds.loisTelemetry (WildsTelemetry) is patterned on, and for listening to
the live DeVeny topic during testing.

Schema reference:
  https://github.com/LowellObservatory/ligmos/blob/master/ligmos/schemas/deveny.loisTelemetry.xsd

Every element is minOccurs="0" in the XSD, so all fields are optional.
"""

from pydantic_xml import BaseXmlModel, element


class DevenyTelemetry(BaseXmlModel, tag="DevenyTelemetry"):
    TimeStamp: int | None = element(default=None)  # Unix epoch seconds

    # --- Calibration lamps (Cd, Ar, Ne, Hg) ---
    Lamp1Name: str | None = element(default=None)
    Lamp1State: bool | None = element(default=None)
    Lamp2Name: str | None = element(default=None)
    Lamp2State: bool | None = element(default=None)
    Lamp3Name: str | None = element(default=None)
    Lamp3State: bool | None = element(default=None)
    Lamp4Name: str | None = element(default=None)
    Lamp4State: bool | None = element(default=None)

    # --- Slit ---
    SlitWidthMM: float | None = element(default=None)  # 0.075–15 mm
    SlitWidthASEC: float | None = element(default=None)  # arcseconds on sky

    # --- Spectrograph optics ---
    GratingTilt: float | None = element(default=None)  # 0–47 degrees
    CollimatorFocus: float | None = element(default=None)  # 7.75–19 mm
    Grating: str | None = element(default=None)  # from MasterInstrumentConfiguration.xml
    RearFilter: str | None = element(default=None)  # from MasterInstrumentConfiguration.xml
