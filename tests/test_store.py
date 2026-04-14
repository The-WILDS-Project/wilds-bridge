"""
Unit tests for TelemetryStore.
No network required.
"""

from wilds.bridge.store import TelemetryStore
from wilds.bridge.models.tcs_telemetry import TcsTelemetry
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.models.wrs_telemetry import WrsTelemetry
from wilds.bridge.models.wilds_telemetry import WildsTelemetry

from .fixtures import (
    TCS_TELEMETRY_XML,
    TCS_STATUS_XML,
    WRS_TELEMETRY_XML,
    WILDS_TELEMETRY_XML,
)


class TestTelemetryStore:
    def test_defaults_all_none(self):
        store = TelemetryStore()
        assert store.tcs is None
        assert store.tcs_status is None
        assert store.wrs is None
        assert store.wilds is None

    def test_assign_tcs(self):
        store = TelemetryStore()
        t = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        store.tcs = t
        assert store.tcs is t
        assert store.tcs.Timestamp == 1733652000

    def test_assign_tcs_status(self):
        store = TelemetryStore()
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        store.tcs_status = s
        assert store.tcs_status is s
        assert store.tcs_status.tcsHealth == "GOOD"

    def test_assign_wrs(self):
        store = TelemetryStore()
        w = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        store.wrs = w
        assert store.wrs is w

    def test_assign_wilds(self):
        store = TelemetryStore()
        w = WildsTelemetry.from_xml(WILDS_TELEMETRY_XML)
        store.wilds = w
        assert store.wilds is w
        assert store.wilds.SlitPositionMM == 12.5

    def test_clear_resets_all(self):
        store = TelemetryStore()
        store.tcs = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        store.tcs_status = TcsStatus.from_xml(TCS_STATUS_XML)
        store.wrs = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        store.wilds = WildsTelemetry.from_xml(WILDS_TELEMETRY_XML)

        store.clear()

        assert store.tcs is None
        assert store.tcs_status is None
        assert store.wrs is None
        assert store.wilds is None

    def test_overwrite_replaces_value(self):
        store = TelemetryStore()
        t1 = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        store.tcs = t1
        t2 = TcsTelemetry.from_xml(TCS_TELEMETRY_XML.replace(
            "<Timestamp>1733652000</Timestamp>",
            "<Timestamp>1733652001</Timestamp>",
        ))
        store.tcs = t2
        assert store.tcs.Timestamp == 1733652001
