"""
Shared type aliases for model field annotations.

Import from here rather than repeating Literal declarations across models.
"""

from typing import Literal

# TCS offset command fields
OffsetNum = Literal["User", "Handset"]
OffsetType = Literal["TPLANE", "SIMPLE"]

# TCS / AOS state enumerations
TcsHealth = Literal["GOOD", "WARNING", "BAD"]
TcsState = Literal["STANDBY", "OFF", "ENABLED", "DISABLED", "FAULT"]

# Coordinate frame
CoordFrame = Literal["FK4", "FK5", "APPT", "GAPPT", "AZEL"]

# Hardware positions
CoverState = Literal["Open", "Closed", "PartiallyOpen", "Unknown"]
FoldMirrorState = Literal["Unknown", "Home", "Extended"]

# New-science-target command fields
EquinoxPrefix = Literal["J", "B"]
RotatorFrame = Literal["Fixed", "Target"]

# wilds-control: slit and ADC
SlitMoveMode = Literal["abs", "jog"]
AdcIndex = Literal[1, 2]
