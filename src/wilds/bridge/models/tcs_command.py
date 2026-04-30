"""
pydantic-xml models for TCS commands.

Publish to:
  TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV

Listen for reply on:
  TCS.TCSSharedVariables.TCSLowLevelStatusSV.TCSTcsCommandResponseSV

commandID per LIG spec: microseconds since midnight UT.
  round((now.hour*3600 + now.minute*60 + now.second + now.microsecond/1e6) * 1e6)

Command types (root tag varies):
  <scienceTargetOffset>    — apply RA/Dec or Az/El offset (arcsec)
  <scienceTargetClearOffset> — set offsets back to 0, 0
  <scienceTargetAbsorbOffset> — bake offset into target coords and clear

offsetType: "TPLANE" (tangent plane, arcsec) or "SIMPLE" (RA in seconds, Dec in arcsec)
num1/num2:  "User" (dither grid) or "Handset" (acquisition tweaks)
"""

import datetime

from pydantic_xml import BaseXmlModel, element

from .types import OffsetNum, OffsetType


def _make_command_id() -> int:
    now = datetime.datetime.now(datetime.UTC)
    return round(
        (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) * 1e6
    )


class _TcsErrorResponse(BaseXmlModel):
    """Placeholder sent with commands; TCS fills it in on the reply."""

    code: int = element(default=0)
    source: str | None = element(default=None)
    status: bool = element(default=False)


class _OffsetDef(BaseXmlModel):
    num1: OffsetNum = element(default="User")
    off1: float = element()                                        # RA or Az component, arcsec
    off2: float = element()                                        # Dec or El component, arcsec
    offsetType: OffsetType = element(default="TPLANE")


class TcsOffsetCommand(BaseXmlModel, tag="scienceTargetOffset"):
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    offsetDef: _OffsetDef = element()

    @classmethod
    def make_offset(
        cls,
        off1: float,
        off2: float,
        offset_type: OffsetType = "TPLANE",
        num1: OffsetNum = "User",
    ) -> "TcsOffsetCommand":
        return cls(
            commandID=_make_command_id(),
            offsetDef=_OffsetDef(off1=off1, off2=off2, offsetType=offset_type, num1=num1),
        )


class TcsClearOffsetCommand(BaseXmlModel, tag="scienceTargetClearOffset"):
    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    num2: OffsetNum = element(default="User")

    @classmethod
    def make(cls, num2: OffsetNum = "User") -> "TcsClearOffsetCommand":
        return cls(commandID=_make_command_id(), num2=num2)


class TcsAbsorbOffsetCommand(BaseXmlModel, tag="scienceTargetAbsorbOffset"):
    """Bakes the current offset into the target coordinates and clears it."""

    commandID: int = element()
    tcsErrorResponse: _TcsErrorResponse = element(default_factory=_TcsErrorResponse)
    num2: OffsetNum = element(default="User")

    @classmethod
    def make(cls, num2: OffsetNum = "User") -> "TcsAbsorbOffsetCommand":
        return cls(commandID=_make_command_id(), num2=num2)
