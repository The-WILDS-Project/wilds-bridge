"""
pydantic-xml models for TCS offset commands.

Publish to:
  TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV

Listen for reply on:
  TCS.TCSSharedVariables.TCSLowLevelStatusSV.TCSTcsCommandResponseSV

commandID construction per LIG spec:
  microseconds since midnight UT
  round((now.hour*3600 + now.minute*60 + now.second + now.microsecond/1e6) * 1e6)

Example command XML:
  <TCSTcsCommand>
    <commandID>59909236</commandID>
    <newTarget>
      <tcsId>0</tcsId>
      <isNewTarget>false</isNewTarget>
    </newTarget>
    <offset>
      <offsetDef>User</offsetDef>
      <off1>-8.133</off1>
      <off2>12.0</off2>
      <offsetType>TPLANE</offsetType>
    </offset>
  </TCSTcsCommand>
"""

import datetime
from pydantic_xml import BaseXmlModel, element


class _NewTarget(BaseXmlModel):
    tcsId: int = element(default=0)
    isNewTarget: bool = element(default=False)


class TcsOffset(BaseXmlModel):
    # "User" or "Handset"
    offsetDef: str = element(default="User")
    # RA or Az component in arcseconds
    off1: float = element()
    # Dec or El component in arcseconds
    off2: float = element()
    # "TPLANE" (tangent plane) or "SIMPLE"
    offsetType: str = element(default="TPLANE")


class TcsCommand(BaseXmlModel, tag="TCSTcsCommand"):
    commandID: int = element()
    newTarget: _NewTarget = element(default_factory=_NewTarget)
    offset: TcsOffset = element()

    @classmethod
    def make_offset(cls, off1: float, off2: float, offset_type: str = "TPLANE") -> "TcsCommand":
        """
        Build a TCS offset command with a correct commandID (µs since midnight UT).
        off1: RA or Az offset in arcseconds
        off2: Dec or El offset in arcseconds
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        command_id = round(
            (now.hour * 3600 + now.minute * 60 + now.second + now.microsecond / 1e6) * 1e6
        )
        return cls(
            commandID=command_id,
            offset=TcsOffset(off1=off1, off2=off2, offsetType=offset_type),
        )
