"""
Unit tests for LDTBroker internal logic.

Tests _is_duplicate() and _parse() directly — no STOMP connection needed.
LDTBroker is instantiated but start() is never called, so no asyncio
tasks or sockets are opened.
"""

import pytest

from wilds.bridge.broker import LDTBroker
from wilds.bridge.config import (
    TOPIC_AOS_DATA_PACKET,
    TOPIC_INSTRUMENT_CUBE,
    TOPIC_TCS_STATUS,
    TOPIC_TCS_TELEMETRY,
    TOPIC_WILDS_TELEMETRY,
    TOPIC_WRS_DATA_PACKET,
    TOPIC_WRS_TELEMETRY,
)
from wilds.bridge.models.aos_data_packet import AosDataPacket
from wilds.bridge.models.instrument_cube_telemetry import InstrumentCubeTelemetry
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.models.tcs_telemetry import TcsTelemetry
from wilds.bridge.models.wilds_telemetry import WildsTelemetry
from wilds.bridge.models.wrs_data_packet import WrsDataPacket
from wilds.bridge.models.wrs_telemetry import WrsTelemetry

from .fixtures import (
    AOS_DATA_PACKET_XML,
    INSTRUMENT_CUBE_XML,
    TCS_STATUS_XML,
    TCS_TELEMETRY_XML,
    WILDS_TELEMETRY_XML,
    WRS_DATA_PACKET_XML,
    WRS_TELEMETRY_XML,
)


@pytest.fixture
def broker():
    return LDTBroker()


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


class TestDedup:
    def test_first_message_not_duplicate(self, broker):
        assert broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-a") is False

    def test_same_body_is_duplicate(self, broker):
        broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-a")
        assert broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-a") is True

    def test_different_body_not_duplicate(self, broker):
        broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-a")
        assert broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-b") is False

    def test_same_body_different_topic_not_duplicate(self, broker):
        broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-a")
        assert broker._is_duplicate(TOPIC_WRS_TELEMETRY, "body-a") is False

    def test_cache_eviction(self, broker):
        """
        After dedup_cache_size + 1 unique messages the oldest hash is evicted
        and the same body is no longer considered a duplicate.
        A deque(maxlen=N) evicts the head only when the (N+1)th item is appended.
        """
        cache_size = broker._cfg.dedup_cache_size  # 4 by default
        # Fill cache, then add one more to push body-0 out
        for i in range(cache_size + 1):
            broker._is_duplicate(TOPIC_TCS_TELEMETRY, f"body-{i}")
        # body-0 is now evicted; sending it again is not a duplicate
        assert broker._is_duplicate(TOPIC_TCS_TELEMETRY, "body-0") is False

    def test_last_message_still_duplicate_after_fill(self, broker):
        cache_size = broker._cfg.dedup_cache_size
        for i in range(cache_size):
            broker._is_duplicate(TOPIC_TCS_TELEMETRY, f"body-{i}")
        # The most-recent message is still in cache
        last = f"body-{cache_size - 1}"
        assert broker._is_duplicate(TOPIC_TCS_TELEMETRY, last) is True


# ---------------------------------------------------------------------------
# Parse routing
# ---------------------------------------------------------------------------


class TestParse:
    def test_tcs_telemetry(self, broker):
        result = broker._parse(TOPIC_TCS_TELEMETRY, TCS_TELEMETRY_XML)
        assert isinstance(result, TcsTelemetry)
        assert result.TimeStamp == 1733652000

    def test_tcs_status(self, broker):
        result = broker._parse(TOPIC_TCS_STATUS, TCS_STATUS_XML)
        assert isinstance(result, TcsStatus)
        assert result.tcsHealth == "GOOD"
        assert result.heartbeat == 100

    def test_wrs_telemetry(self, broker):
        result = broker._parse(TOPIC_WRS_TELEMETRY, WRS_TELEMETRY_XML)
        assert isinstance(result, WrsTelemetry)

    def test_wrs_data_packet(self, broker):
        result = broker._parse(TOPIC_WRS_DATA_PACKET, WRS_DATA_PACKET_XML)
        assert isinstance(result, WrsDataPacket)
        assert result.airTemp_C is not None

    def test_aos_data_packet(self, broker):
        result = broker._parse(TOPIC_AOS_DATA_PACKET, AOS_DATA_PACKET_XML)
        assert isinstance(result, AosDataPacket)
        assert result.totalFocusOffset is not None

    def test_instrument_cube(self, broker):
        result = broker._parse(TOPIC_INSTRUMENT_CUBE, INSTRUMENT_CUBE_XML)
        assert isinstance(result, InstrumentCubeTelemetry)
        assert result.TimeStamp == 1581440388

    def test_wilds_telemetry(self, broker):
        result = broker._parse(TOPIC_WILDS_TELEMETRY, WILDS_TELEMETRY_XML)
        assert isinstance(result, WildsTelemetry)

    def test_unknown_topic_returns_raw_string(self, broker):
        result = broker._parse("some.unknown.topic", "<foo>bar</foo>")
        assert result == "<foo>bar</foo>"

    def test_malformed_xml_returns_none(self, broker):
        result = broker._parse(TOPIC_TCS_TELEMETRY, "this is not xml")
        assert result is None

    def test_wrong_root_tag_returns_none(self, broker):
        result = broker._parse(TOPIC_TCS_TELEMETRY, "<wrong>data</wrong>")
        assert result is None


# ---------------------------------------------------------------------------
# Store update
# ---------------------------------------------------------------------------


class TestUpdateStore:
    def test_tcs_updates_store(self, broker):
        t = TcsTelemetry.from_xml(TCS_TELEMETRY_XML)
        broker._update_store(TOPIC_TCS_TELEMETRY, t)
        assert broker.store.tcs is t

    def test_tcs_status_updates_store(self, broker):
        s = TcsStatus.from_xml(TCS_STATUS_XML)
        broker._update_store(TOPIC_TCS_STATUS, s)
        assert broker.store.tcs_status is s

    def test_wrs_updates_store(self, broker):
        w = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        broker._update_store(TOPIC_WRS_TELEMETRY, w)
        assert broker.store.wrs is w

    def test_wrs_packet_updates_store(self, broker):
        w = WrsDataPacket.from_xml(WRS_DATA_PACKET_XML)
        broker._update_store(TOPIC_WRS_DATA_PACKET, w)
        assert broker.store.wrs_packet is w

    def test_aos_updates_store(self, broker):
        a = AosDataPacket.from_xml(AOS_DATA_PACKET_XML)
        broker._update_store(TOPIC_AOS_DATA_PACKET, a)
        assert broker.store.aos is a

    def test_instrument_cube_updates_store(self, broker):
        ic = InstrumentCubeTelemetry.from_xml(INSTRUMENT_CUBE_XML)
        broker._update_store(TOPIC_INSTRUMENT_CUBE, ic)
        assert broker.store.instrument_cube is ic

    def test_wilds_updates_store(self, broker):
        w = WildsTelemetry.from_xml(WILDS_TELEMETRY_XML)
        broker._update_store(TOPIC_WILDS_TELEMETRY, w)
        assert broker.store.wilds is w

    def test_wrong_type_does_not_update(self, broker):
        # Passing a WrsTelemetry to the TCS slot — should be ignored
        w = WrsTelemetry.from_xml(WRS_TELEMETRY_XML)
        broker._update_store(TOPIC_TCS_TELEMETRY, w)
        assert broker.store.tcs is None
