"""
Lenient base for models of messages that LDT publishes and WILDS subscribes to.

The ligmos XSDs (vendored in ``wilds/bridge/schemas``) give only element names,
order and base types — every element is optional, with no enumerations or ranges.
Live messages don't always honour even that: JOE puts "UNKNOWN" in decimal fields
at the start of a night, and state strings arrive in whatever case the publisher
uses (instrumentCube sends "CLOSED"/"HOME").

Inbound models therefore follow the XSD loosely, and this base absorbs the rest:

- Literal fields are matched case-insensitively and returned in the declared
  spelling, so code can branch on e.g. ``TCSState == "ENABLED"``.
- Non-string fields (float, int, bool, datetime) map placeholders ("UNKNOWN",
  empty) to None instead of rejecting the whole message.

Plain ``str`` fields are left untouched, so "UNKNOWN" survives where it is a value.
Use Literal only for fields WILDS acts on; everything else stays ``str``.
"""

from typing import Literal

from pydantic import ValidationInfo, field_validator
from pydantic_xml import BaseXmlModel

_PLACEHOLDERS = {"", "UNKNOWN"}


def _members(annotation: object) -> list[object]:
    """Flatten ``X | Y | None`` and ``Literal[...]`` into their members."""
    if getattr(annotation, "__origin__", None) is Literal:
        return list(getattr(annotation, "__args__", ()))
    if args := getattr(annotation, "__args__", None):
        return [m for a in args for m in _members(a)]
    return [annotation]


class InboundXmlModel(BaseXmlModel):
    @field_validator("*", mode="before")
    @classmethod
    def _lenient(cls, value: object, info: ValidationInfo) -> object:
        if not isinstance(value, str) or info.field_name is None:
            return value
        members = _members(cls.model_fields[info.field_name].annotation)
        text = value.strip()
        folded = text.casefold()
        for m in members:
            if isinstance(m, str) and m.casefold() == folded:
                return m
        if str not in members and text.upper() in _PLACEHOLDERS:
            return None
        return value
