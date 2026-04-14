"""
Unit tests for pydantic-xml model round-trips.

Each test parses a fixture XML string → model, checks key field values,
then serialises back to XML and re-parses to confirm round-trip fidelity.
No network or broker required.
"""

import pytest

from wilds.bridge.models.tcs_telemetry import TcsTelemetry
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.models.wrs_telemetry import WrsTelemetry
from wilds.bridge.models.wilds_telemetry import WildsTelemetry
from wilds.bridge.models.tcs_command import TcsCommand, TcsOffset

from .fixtures import (
    TCS_TELEMETRY_XML,
    TCS_TELEMETRY_XML_MINIMAL,
    TCS_STATUS_XML,
    WRS_TELEMETRY_XML,
    WRS_TELEMETRY_XML_MINIMAL,
    WILDS_TELEMETRY_XML,
    TCS_COMMAND_XML,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def roundtrip(model):
    """Serialise model → XML string → re-parse into same type."""
    xml = model.to_xml(encoding="unicode")
    return type(model).from_xml(xml)


# ---------------------------------------------------------------------------
# TcsTelemetry
# ---------------------------------------------------------------------------

class TestTcsTelemetry:
    def test_parse_full(self):
        t = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        assert t.Timestamp == 1733652000
        assert t.TCSLST == "04:41:18.100"
        assert t.TCSHeartBeat == 42
        assert t.InPosition is True
        assert t.TCSHealth == "GOOD"
        assert t.CurrentParAngle == "-12.34"
        assert t.MountTemperature == "7.5"
        assert t.DomeOccultationWarning is False
        assert t.CLSLowBankState == "On"
        assert t.DSSPositionStatus == "Open"

    def test_parse_minimal_optional_fields_are_none(self):
        t = TcsTelemetry.from_xml(TCS_TELEMETRY_XML_MINIMAL)
        assert t.MountTemperature is None
        assert t.MountDomeAzimuthDifference is None
        assert t.CLSLowBankState is None
        assert t.DSSPositionStatus is None

    def test_roundtrip(self):
        original = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        restored = roundtrip(original)
        assert restored.Timestamp == original.Timestamp
        assert restored.CurrentParAngle == original.CurrentParAngle
        assert restored.InPosition == original.InPosition
        assert restored.MountTemperature == original.MountTemperature

    def test_roundtrip_minimal(self):
        original = TcsTelemetry.from_xml(TCS_TELEMETRY_XML_MINIMAL)
        restored = roundtrip(original)
        assert restored.MountTemperature is None
        assert restored.CLSLowBankState is None


# ---------------------------------------------------------------------------
# TcsStatus
# ---------------------------------------------------------------------------

class TestTcsStatus:
    def test_parse(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        assert s.tcsVersion == "1.8"
        assert s.heartbeat == 100
        assert s.inPositionIsTrue is True
        assert s.tcsHealth == "GOOD"
        assert s.mountGuideMode == "ClosedLoop"

    def test_pointing_positions(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        pp = s.pointingPositions
        assert pp is not None
        assert pp.currentParAngle == pytest.approx(-12.34)
        assert pp.currentRADec.ra.hours == 5
        assert pp.currentRADec.declination.degreesArc == 22
        assert pp.currentRADec.targetName == "Crab Nebula"
        assert pp.currentAzEl.azimuth.degreesArc == 175
        assert pp.currentAzEl.elevation.degreesAlt == 61

    def test_times_and_limits(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        assert s.currentTimes is not None
        assert s.currentTimes.utcTime == "07:00:00.0"
        assert s.limits is not None
        assert s.limits.airmass == pytest.approx(1.143)
        assert s.limits.moonProximity == pytest.approx(45.2)

    def test_roundtrip(self):
        original = TcsStatus.from_xml(TCS_STATUS_XML)
        restored = roundtrip(original)
        assert restored.heartbeat == original.heartbeat
        assert restored.pointingPositions.currentParAngle == pytest.approx(
            original.pointingPositions.currentParAngle
        )

    def test_all_optional_none_when_absent(self):
        xml = "<tcsTCSStatus/>"
        s = TcsStatus.from_xml(xml)
        assert s.tcsVersion is None
        assert s.heartbeat is None
        assert s.pointingPositions is None
        assert s.limits is None


# ---------------------------------------------------------------------------
# WrsTelemetry
# ---------------------------------------------------------------------------

class TestWrsTelemetry:
    def test_parse_full(self):
        w = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        assert w.Timestamp == 1733652000
        assert w.AirTemp == pytest.approx(5.2)
        assert w.BarometricPressure == pytest.approx(820.1)
        assert w.DewPoint == pytest.approx(-3.1)
        assert w.RelativeHumidity == pytest.approx(42.0)
        assert w.WindDirection == pytest.approx(270.0)
        assert w.WindSpeed == pytest.approx(3.5)

    def test_parse_minimal(self):
        w = WrsTelemetry.from_xml(WRS_TELEMETRY_XML_MINIMAL)
        assert w.Timestamp == 1733652001
        assert w.AirTemp is None
        assert w.WindSpeed is None

    def test_roundtrip(self):
        original = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        restored = roundtrip(original)
        assert restored.AirTemp == pytest.approx(original.AirTemp)
        assert restored.WindSpeed == pytest.approx(original.WindSpeed)


# ---------------------------------------------------------------------------
# WildsTelemetry
# ---------------------------------------------------------------------------

class TestWildsTelemetry:
    def test_parse(self):
        w = WildsTelemetry.from_xml(WILDS_TELEMETRY_XML)
        assert w.Timestamp == 1733652000
        assert w.SlitPositionMM == pytest.approx(12.5)
        assert w.SlitPositionASEC == pytest.approx(1.25)
        assert w.ADC1PositionMM == pytest.approx(5.0)
        assert w.ADCParAngleDeg == pytest.approx(-12.34)
        assert w.Shutter1State == "Open"
        assert w.VISExposureState == "EXPOSING"
        assert w.VISCCDTemp == pytest.approx(-110.0)
        assert w.LastFITSFileVIS == "/data/wilds/2024/vis_001.fits"

    def test_roundtrip(self):
        original = WildsTelemetry.from_xml(WILDS_TELEMETRY_XML)
        restored = roundtrip(original)
        assert restored.SlitPositionMM == pytest.approx(original.SlitPositionMM)
        assert restored.LastFITSFileUV == original.LastFITSFileUV

    def test_now_constructor(self):
        w = WildsTelemetry.now(SlitPositionMM=5.0, VISExposureState="IDLE")
        assert w.Timestamp > 0
        assert w.SlitPositionMM == pytest.approx(5.0)
        assert w.VISExposureState == "IDLE"
        assert w.UVExposureState is None

    def test_defaults_all_none(self):
        w = WildsTelemetry.now()
        assert w.SlitPositionMM is None
        assert w.ADC1PositionMM is None
        assert w.Shutter1State is None


# ---------------------------------------------------------------------------
# TcsCommand / TcsOffset
# ---------------------------------------------------------------------------

class TestTcsCommand:
    def test_parse(self):
        cmd = TcsCommand.from_xml(TCS_COMMAND_XML)
        assert cmd.commandID == 59909236
        assert cmd.offset.off1 == pytest.approx(-8.133)
        assert cmd.offset.off2 == pytest.approx(12.0)
        assert cmd.offset.offsetType == "TPLANE"
        assert cmd.offset.offsetDef == "User"
        assert cmd.newTarget.tcsId == 0
        assert cmd.newTarget.isNewTarget is False

    def test_roundtrip(self):
        original = TcsCommand.from_xml(TCS_COMMAND_XML)
        restored = roundtrip(original)
        assert restored.commandID == original.commandID
        assert restored.offset.off1 == pytest.approx(original.offset.off1)
        assert restored.offset.off2 == pytest.approx(original.offset.off2)
