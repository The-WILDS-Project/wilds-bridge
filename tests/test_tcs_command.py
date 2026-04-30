"""
Unit tests for TcsOffsetCommand.make_offset().

Validates commandID construction (µs since midnight UT per LIG spec)
and that the resulting object serialises cleanly.
No network required.
"""

import pytest

from wilds.bridge.models.tcs_command import TcsOffsetCommand

_MAX_COMMAND_ID = 86_400 * 1_000_000  # µs in one day


class TestMakeOffset:
    def test_commandid_positive(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd.commandID > 0

    def test_commandid_within_day(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd.commandID < _MAX_COMMAND_ID

    def test_commandid_is_int(self):
        cmd = TcsOffsetCommand.make_offset(-8.133, 12.0)
        assert isinstance(cmd.commandID, int)

    def test_offsets_preserved(self):
        cmd = TcsOffsetCommand.make_offset(-8.133, 12.0)
        assert cmd.offsetDef.off1 == pytest.approx(-8.133)
        assert cmd.offsetDef.off2 == pytest.approx(12.0)

    def test_default_offset_type(self):
        cmd = TcsOffsetCommand.make_offset(1.0, 2.0)
        assert cmd.offsetDef.offsetType == "TPLANE"

    def test_custom_offset_type(self):
        cmd = TcsOffsetCommand.make_offset(1.0, 2.0, offset_type="SIMPLE")
        assert cmd.offsetDef.offsetType == "SIMPLE"

    def test_default_num1_user(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd.offsetDef.num1 == "User"

    def test_handset_num1(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0, num1="Handset")
        assert cmd.offsetDef.num1 == "Handset"

    def test_error_response_defaults(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd.tcsErrorResponse.code == 0
        assert cmd.tcsErrorResponse.status is False

    def test_successive_commands_nondecreasing(self):
        cmd1 = TcsOffsetCommand.make_offset(0.0, 0.0)
        cmd2 = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd2.commandID >= cmd1.commandID

    def test_xml_roundtrip(self):
        cmd = TcsOffsetCommand.make_offset(-8.133, 12.0)
        xml = cmd.to_xml(encoding="unicode")
        restored = TcsOffsetCommand.from_xml(xml)
        assert restored.commandID == cmd.commandID
        assert restored.offsetDef.off1 == pytest.approx(cmd.offsetDef.off1)
        assert restored.offsetDef.off2 == pytest.approx(cmd.offsetDef.off2)
        assert restored.offsetDef.offsetType == cmd.offsetDef.offsetType

    def test_xml_contains_correct_tags(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        xml = str(cmd.to_xml(encoding="unicode"))
        assert "<scienceTargetOffset>" in xml
        assert "<commandID>" in xml
        assert "<offsetDef>" in xml
        assert "<tcsErrorResponse>" in xml

    def test_zero_offsets(self):
        cmd = TcsOffsetCommand.make_offset(0.0, 0.0)
        assert cmd.offsetDef.off1 == pytest.approx(0.0)
        assert cmd.offsetDef.off2 == pytest.approx(0.0)

    def test_large_offsets(self):
        cmd = TcsOffsetCommand.make_offset(3600.0, -3600.0)
        assert cmd.offsetDef.off1 == pytest.approx(3600.0)
        assert cmd.offsetDef.off2 == pytest.approx(-3600.0)
