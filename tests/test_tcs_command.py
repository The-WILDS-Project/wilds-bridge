"""
Unit tests for TcsCommand.make_offset().

Validates commandID construction (µs since midnight UT per LIG spec)
and that the resulting object serialises cleanly.
No network required.
"""

import datetime

import pytest

from wilds.bridge.models.tcs_command import TcsCommand, TcsOffset


_MAX_COMMAND_ID = 86_400 * 1_000_000   # µs in one day


class TestMakeOffset:
    def test_commandid_positive(self):
        cmd = TcsCommand.make_offset(0.0, 0.0)
        assert cmd.commandID > 0

    def test_commandid_within_day(self):
        cmd = TcsCommand.make_offset(0.0, 0.0)
        assert cmd.commandID < _MAX_COMMAND_ID

    def test_commandid_is_int(self):
        cmd = TcsCommand.make_offset(-8.133, 12.0)
        assert isinstance(cmd.commandID, int)

    def test_offsets_preserved(self):
        cmd = TcsCommand.make_offset(-8.133, 12.0)
        assert cmd.offset.off1 == pytest.approx(-8.133)
        assert cmd.offset.off2 == pytest.approx(12.0)

    def test_default_offset_type(self):
        cmd = TcsCommand.make_offset(1.0, 2.0)
        assert cmd.offset.offsetType == "TPLANE"

    def test_custom_offset_type(self):
        cmd = TcsCommand.make_offset(1.0, 2.0, offset_type="SIMPLE")
        assert cmd.offset.offsetType == "SIMPLE"

    def test_default_new_target_false(self):
        cmd = TcsCommand.make_offset(0.0, 0.0)
        assert cmd.newTarget.isNewTarget is False
        assert cmd.newTarget.tcsId == 0

    def test_successive_commands_nondecreasing(self):
        """Two commands made in sequence should have non-decreasing IDs."""
        cmd1 = TcsCommand.make_offset(0.0, 0.0)
        cmd2 = TcsCommand.make_offset(0.0, 0.0)
        assert cmd2.commandID >= cmd1.commandID

    def test_xml_roundtrip(self):
        cmd = TcsCommand.make_offset(-8.133, 12.0)
        xml = cmd.to_xml(encoding="unicode")
        restored = TcsCommand.from_xml(xml)
        assert restored.commandID == cmd.commandID
        assert restored.offset.off1 == pytest.approx(cmd.offset.off1)
        assert restored.offset.off2 == pytest.approx(cmd.offset.off2)
        assert restored.offset.offsetType == cmd.offset.offsetType

    def test_xml_contains_tag(self):
        cmd = TcsCommand.make_offset(0.0, 0.0)
        xml = cmd.to_xml(encoding="unicode")
        assert "<TCSTcsCommand>" in xml
        assert "<commandID>" in xml
        assert "<offset>" in xml

    def test_zero_offsets(self):
        cmd = TcsCommand.make_offset(0.0, 0.0)
        assert cmd.offset.off1 == pytest.approx(0.0)
        assert cmd.offset.off2 == pytest.approx(0.0)

    def test_large_offsets(self):
        cmd = TcsCommand.make_offset(3600.0, -3600.0)
        assert cmd.offset.off1 == pytest.approx(3600.0)
        assert cmd.offset.off2 == pytest.approx(-3600.0)
