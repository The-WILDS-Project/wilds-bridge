"""
Unit tests for TcsOffsetCommand.make_offset() and TcsScienceTargetCommand.make().

Validates commandID construction (µs since midnight UT per LIG spec)
and that the resulting object serialises cleanly.
No network required.
"""

import pytest

from wilds.bridge.models.tcs_command import (
    TcsNewScienceTarget,
    TcsOffsetCommand,
    TcsScienceTargetCommand,
)

from .fixtures import NEW_SCIENCE_TARGET_XML

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


class TestScienceTarget:
    def test_rotator_frame_defaults_to_target(self):
        # Matches the TCS default: the field holds still on the slit at rot_pa.
        cmd = TcsScienceTargetCommand.make("M31", 0.7123, 41.27)
        assert cmd.rotator.rotatorFrame == "Target"
        assert cmd.rotator.rotPA == pytest.approx(0.0)

    def test_rotator_settings_serialised(self):
        cmd = TcsScienceTargetCommand.make("M31", 0.7123, 41.27, rot_pa=96.3, rot_frame="Fixed")
        xml = cmd.to_xml(encoding="unicode")
        assert "<rotPA>96.3</rotPA>" in xml
        assert "<rotatorFrame>Fixed</rotatorFrame>" in xml

    def test_root_is_science_target_configuration(self):
        # The command on TCSTcsCommandSV, not the <newScienceTarget> telemetry wrapper.
        xml = str(TcsScienceTargetCommand.make("M31", 0.7123, 41.27).to_xml(encoding="unicode"))
        assert xml.startswith("<scienceTargetConfiguration>")
        assert "<newScienceTarget>" not in xml
        assert "<commandID>" in xml
        assert "<tcsErrorResponse>" in xml

    def test_commandid_within_day(self):
        cmd = TcsScienceTargetCommand.make("M31", 0.7123, 41.27)
        assert 0 < cmd.commandID < _MAX_COMMAND_ID

    def test_extracted_from_telemetry(self):
        # The TCS reports its current target wrapped in <newScienceTarget>; the inner
        # configuration is a ready command, the basis for re-sending with a new rotator.
        sent = TcsScienceTargetCommand.make("M31", 0.7123, 41.27, rot_pa=96.3)
        report = TcsNewScienceTarget(
            demandRADec=sent.target.raDecParameters, scienceTargetConfiguration=sent
        )
        parsed = TcsNewScienceTarget.from_xml(report.to_xml(encoding="unicode"))
        config = parsed.scienceTargetConfiguration
        assert config.target.targetName == "M31"
        assert config.rotator.rotPA == pytest.approx(96.3)
        assert str(config.to_xml(encoding="unicode")).startswith("<scienceTargetConfiguration>")


class TestWithRotator:
    @pytest.fixture
    def current(self):
        return TcsNewScienceTarget.from_xml(NEW_SCIENCE_TARGET_XML).scienceTargetConfiguration

    def test_report_parses_despite_element_order(self, current):
        # The report orders tcsErrorResponse status/code/source; ours is code/source/status.
        assert current.tcsErrorResponse.code == 0
        assert current.tcsErrorResponse.status is False

    def test_only_rotator_changes(self, current):
        cmd = current.with_rotator(120.0)
        assert cmd.rotator.rotPA == pytest.approx(120.0)
        assert cmd.target == current.target
        assert cmd.wl_microns == current.wl_microns
        assert cmd.fracrate == current.fracrate
        assert cmd.targetConfigName == current.targetConfigName

    def test_differential_rates_kept(self, current):
        cmd = current.with_rotator(120.0)
        assert cmd.target.difftrack.dRA_ArcsPS == pytest.approx(0.01)
        assert cmd.target.difftrack.dDec_ArcsPS == pytest.approx(-0.02)

    def test_frame_kept_unless_given(self, current):
        assert current.with_rotator(10.0).rotator.rotatorFrame == "Target"
        assert current.with_rotator(10.0, "Fixed").rotator.rotatorFrame == "Fixed"

    def test_pa_normalised(self, current):
        assert current.with_rotator(-30.0).rotator.rotPA == pytest.approx(330.0)
        assert current.with_rotator(360.0).rotator.rotPA == pytest.approx(0.0)

    def test_fresh_command_id(self, current):
        cmd = current.with_rotator(120.0)
        assert cmd.commandID != current.commandID
        assert 0 < cmd.commandID < _MAX_COMMAND_ID

    def test_original_untouched(self, current):
        current.with_rotator(120.0)
        assert current.rotator.rotPA == pytest.approx(30.0)

    def test_serialises_as_command(self, current):
        xml = str(current.with_rotator(120.0).to_xml(encoding="unicode"))
        assert xml.startswith("<scienceTargetConfiguration>")
        assert "<rotPA>120.0</rotPA>" in xml
        assert "<targetName>Crab Nebula</targetName>" in xml
