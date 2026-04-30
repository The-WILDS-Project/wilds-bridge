"""
Unit tests for pydantic-xml model round-trips.

Each test parses a fixture XML string → model, checks key field values,
then serialises back to XML and re-parses to confirm round-trip fidelity.
No network or broker required.
"""

import pytest

from wilds.bridge.models.aos_data_packet import AosDataPacket
from wilds.bridge.models.instrument_cube_telemetry import InstrumentCubeTelemetry
from wilds.bridge.models.tcs_command import TcsClearOffsetCommand, TcsOffsetCommand
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.models.tcs_telemetry import TcsTelemetry
from wilds.bridge.models.wilds_telemetry import WildsTelemetry
from wilds.bridge.models.wrs_data_packet import WrsDataPacket
from wilds.bridge.models.wrs_telemetry import WrsTelemetry

from .fixtures import (
    AOS_DATA_PACKET_XML,
    INSTRUMENT_CUBE_XML,
    TCS_CLEAR_OFFSET_XML,
    TCS_OFFSET_COMMAND_XML,
    TCS_STATUS_XML,
    TCS_TELEMETRY_XML,
    TCS_TELEMETRY_XML_MINIMAL,
    WILDS_TELEMETRY_XML,
    WRS_DATA_PACKET_XML,
    WRS_TELEMETRY_XML,
    WRS_TELEMETRY_XML_MINIMAL,
)


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
        assert t.TimeStamp == 1733652000
        assert t.TCSLST == "04:41:18.100"
        assert t.TCSHeartBeat == 42
        assert t.InPosition is True
        assert t.TCSHealth == "GOOD"
        assert t.MountGuideMode == "ClosedLoop"
        assert t.CurrentParAngle == "-12.34"
        assert t.TCSCurrentRotatorPA == "90.0"
        assert t.TCSCurrentRotatorIAA == "4.95"
        assert t.MountTemperature == "7.5"
        assert t.DomeOccultationWarning is False
        assert t.CLSLowBankState == "On"
        assert t.DSSPositionStatus == "Open"

    def test_parse_minimal_optional_fields_are_none(self):
        t = TcsTelemetry.from_xml(TCS_TELEMETRY_XML_MINIMAL)
        assert t.MountTemperature is None
        assert t.MountDomeAzimuthDifference is None
        assert t.MountGuideMode is None
        assert t.CLSLowBankState is None
        assert t.DSSPositionStatus is None

    def test_roundtrip(self):
        original = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        restored = roundtrip(original)
        assert restored.TimeStamp == original.TimeStamp
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
        assert s.tcsVersion == "V1.9"
        assert s.heartbeat == 100
        assert s.azCurrentWrap == -1
        assert s.rotCurrentWrap == -1
        assert s.inPositionIsTrue is True
        assert s.tcsHealth == "GOOD"
        assert s.mountGuideMode == "ClosedLoop"
        assert s.axesTrackMode == "All"
        assert s.inPositionAzIsTrue is True

    def test_pointing_positions(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        pp = s.pointingPositions
        assert pp is not None
        assert pp.currentParAngle == pytest.approx(-12.34)
        assert pp.currentRADec.ra.hours == 5
        assert pp.currentRADec.declination.degreesDec == "22"
        assert pp.targetName == "Crab Nebula"
        assert pp.currentAzEl.azimuth.degreesArc == 175
        assert pp.currentAzEl.elevation.degreesAlt == 61
        assert pp.currentRotatorPositions.rotPA == pytest.approx(225.8)

    def test_times_and_limits(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        assert s.currentTimes is not None
        assert s.currentTimes.lst.hours == 4
        assert s.currentTimes.time == "2026-04-29T07:00:00.000+00:00"
        assert s.limits is not None
        assert s.limits.airmass == pytest.approx(1.143)
        assert s.limits.moonProximity.distance_deg == pytest.approx(45.2)
        assert s.limits.zenith.currentZD_deg == pytest.approx(28.5)

    def test_offset_status(self):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        assert s.offsetStatus is not None
        assert s.offsetStatus.offsetType == "SIMPLE"
        assert s.offsetStatus.handsetOff1 == pytest.approx(0.4)

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
# WrsTelemetry (stub model, wrs.loisTelemetry)
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
# WrsDataPacket (WRS.WRSPubDataSV.WRSDataPacket — metric, authoritative)
# ---------------------------------------------------------------------------


class TestWrsDataPacket:
    def test_parse(self):
        w = WrsDataPacket.from_xml(WRS_DATA_PACKET_XML)
        assert w.airTemp_C == pytest.approx(7.3)
        assert w.barPressure_mbar == pytest.approx(1025.0)
        assert w.dewPointCurrentValue == pytest.approx(-2.1)
        assert w.relativeHumidity == pytest.approx(28.0)
        assert w.windSpeed == pytest.approx(3.2)
        assert w.windDirection_deg == pytest.approx(294.0)
        assert w.tenMinWindGustSpeed == pytest.approx(5.8)
        assert w.timestamp == "2018-09-29T01:43:29.000+00:00"

    def test_statistics(self):
        w = WrsDataPacket.from_xml(WRS_DATA_PACKET_XML)
        assert w.temperatureStatistics is not None
        assert w.temperatureStatistics.max == pytest.approx(9.1)
        assert w.temperatureStatistics.min == pytest.approx(6.8)
        assert w.windSpeedStatistics is not None
        assert w.windSpeedStatistics.mean == pytest.approx(3.4)

    def test_minimal(self):
        w = WrsDataPacket.from_xml("<WRSDataPacket/>")
        assert w.airTemp_C is None
        assert w.windSpeed is None
        assert w.temperatureStatistics is None

    def test_roundtrip(self):
        original = WrsDataPacket.from_xml(WRS_DATA_PACKET_XML)
        restored = roundtrip(original)
        assert restored.airTemp_C == pytest.approx(original.airTemp_C)
        assert restored.windSpeed == pytest.approx(original.windSpeed)
        assert restored.temperatureStatistics.max == pytest.approx(
            original.temperatureStatistics.max
        )


# ---------------------------------------------------------------------------
# AosDataPacket
# ---------------------------------------------------------------------------


class TestAosDataPacket:
    def test_parse(self):
        a = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        assert a.summaryState == "Enabled"
        assert a.detailedState == "ClosedLoopState"
        assert a.totalFocusOffset == pytest.approx(0.001195)
        assert a.focusOffsetDemandOutOfRange is False
        assert a.wavefrontDataOutOfRange is False
        assert a.timestamp == "2018-09-29T06:09:34.662+00:00"

    def test_m2_piston(self):
        a = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        assert a.tipTiltPistonDemandM2 is not None
        assert a.tipTiltPistonDemandM2.Piston_m == pytest.approx(0.000416)
        assert a.tipTiltPistonDemandM2.X_Tilt_rad == pytest.approx(-0.000211)

    def test_coma_offset(self):
        a = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        assert a.comaPointingOffset is not None
        assert a.comaPointingOffset.xCorrection_arcsec == pytest.approx(-23.49)

    def test_settled_flags(self):
        a = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        assert a.M1FSettled is True
        assert a.M2PSettled is True
        assert a.M2VSettled is True

    def test_minimal(self):
        a = AosDataPacket.from_xml("<AOSDataPacket/>")
        assert a.totalFocusOffset is None
        assert a.summaryState is None
        assert a.M1FSettled is None

    def test_roundtrip(self):
        original = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        restored = roundtrip(original)
        assert restored.totalFocusOffset == pytest.approx(original.totalFocusOffset)
        assert restored.summaryState == original.summaryState


# ---------------------------------------------------------------------------
# InstrumentCubeTelemetry
# ---------------------------------------------------------------------------


class TestInstrumentCubeTelemetry:
    def test_parse(self):
        ic = InstrumentCubeTelemetry.from_xml(INSTRUMENT_CUBE_XML)
        assert ic.TimeStamp == 1581440388
        assert ic.InstrumentCoverState == "Open"
        assert ic.InstrumentCoverPosition == pytest.approx(-3.22)
        assert ic.FMAState == "Home"
        assert ic.FMAPosition == pytest.approx(0.0)
        assert ic.FMCState == "Extended"
        assert ic.FMCPosition == pytest.approx(12.5)

    def test_minimal(self):
        ic = InstrumentCubeTelemetry.from_xml("<InstrumentCubeTelemetry/>")
        assert ic.TimeStamp is None
        assert ic.InstrumentCoverState is None
        assert ic.FMAState is None

    def test_roundtrip(self):
        original = InstrumentCubeTelemetry.from_xml(INSTRUMENT_CUBE_XML)
        restored = roundtrip(original)
        assert restored.TimeStamp == original.TimeStamp
        assert restored.FMCPosition == pytest.approx(original.FMCPosition)


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
# TcsOffsetCommand / TcsClearOffsetCommand
# ---------------------------------------------------------------------------


class TestTcsOffsetCommand:
    def test_parse(self):
        cmd = TcsOffsetCommand.from_xml(TCS_OFFSET_COMMAND_XML)
        assert cmd.commandID == 59909236
        assert cmd.offsetDef.off1 == pytest.approx(-8.133)
        assert cmd.offsetDef.off2 == pytest.approx(12.0)
        assert cmd.offsetDef.offsetType == "TPLANE"
        assert cmd.offsetDef.num1 == "User"
        assert cmd.tcsErrorResponse.code == 0
        assert cmd.tcsErrorResponse.status is False

    def test_roundtrip(self):
        original = TcsOffsetCommand.from_xml(TCS_OFFSET_COMMAND_XML)
        restored = roundtrip(original)
        assert restored.commandID == original.commandID
        assert restored.offsetDef.off1 == pytest.approx(original.offsetDef.off1)
        assert restored.offsetDef.off2 == pytest.approx(original.offsetDef.off2)


class TestTcsClearOffsetCommand:
    def test_parse(self):
        cmd = TcsClearOffsetCommand.from_xml(TCS_CLEAR_OFFSET_XML)
        assert cmd.commandID == 762271817
        assert cmd.num2 == "User"
        assert cmd.tcsErrorResponse.status is False
