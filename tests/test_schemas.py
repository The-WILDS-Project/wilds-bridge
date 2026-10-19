"""
Check inbound models against the vendored ligmos XSDs and sample messages.

- Every ligmos sample message must parse with its model.
- Models must declare the same elements, in the same order, as their XSD
  (pydantic-xml parses elements in declaration order).
- Our hand-written fixtures must themselves be valid against the XSD.

No network or broker required.
"""

from pathlib import Path

import pytest
import xmlschema

import wilds.bridge
from wilds.bridge.models.aos_data_packet import AosDataPacket
from wilds.bridge.models.deveny_telemetry import DevenyTelemetry
from wilds.bridge.models.inbound import InboundXmlModel
from wilds.bridge.models.instrument_cube_telemetry import InstrumentCubeTelemetry
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.models.tcs_telemetry import TcsTelemetry
from wilds.bridge.models.wrs_data_packet import WrsDataPacket
from wilds.bridge.models.wrs_telemetry import WrsTelemetry

from .fixtures import (
    AOS_DATA_PACKET_XML,
    DEVENY_TELEMETRY_XML,
    INSTRUMENT_CUBE_XML,
    TCS_TELEMETRY_XML,
    TCS_TELEMETRY_XML_MINIMAL,
    WRS_DATA_PACKET_XML,
)

SCHEMAS = Path(wilds.bridge.__path__[0]) / "schemas"
SAMPLES = SCHEMAS / "xmlsamples"
TCS_STATUS_1_8 = "TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV.@1_8"

# (ligmos topic name, model)
SAMPLE_MODELS = [
    ("AOS.AOSPubDataSV.AOSDataPacket", AosDataPacket),
    ("deveny.loisTelemetry", DevenyTelemetry),
    ("instrumentCube.loisTelemetry", InstrumentCubeTelemetry),
    ("tcs.loisTelemetry", TcsTelemetry),
    (TCS_STATUS_1_8, TcsStatus),
    ("WRS.WRSPubDataSV.WRSDataPacket", WrsDataPacket),
    ("wrs.loisTelemetry", WrsTelemetry),
]

# Models that declare every XSD element. TcsStatus is a deliberate subset of v1.9,
# and wrs.loisTelemetry has no XSD.
FULL_MODELS = [
    ("AOS.AOSPubDataSV.AOSDataPacket", AosDataPacket),
    ("deveny.loisTelemetry", DevenyTelemetry),
    ("instrumentCube.loisTelemetry", InstrumentCubeTelemetry),
    ("tcs.loisTelemetry", TcsTelemetry),
    ("WRS.WRSPubDataSV.WRSDataPacket", WrsDataPacket),
]


def schema(topic: str) -> xmlschema.XMLSchema:
    return xmlschema.XMLSchema(SCHEMAS / f"{topic}.xsd")


@pytest.mark.parametrize(("topic", "model"), SAMPLE_MODELS, ids=[t for t, _ in SAMPLE_MODELS])
def test_ligmos_sample_parses(topic, model):
    model.from_xml((SAMPLES / f"{topic}.xml").read_bytes())


@pytest.mark.parametrize(("topic", "model"), FULL_MODELS, ids=[t for t, _ in FULL_MODELS])
def test_model_elements_match_xsd(topic, model):
    xsd = schema(topic)
    (root,) = xsd.elements.values()
    assert model.__xml_tag__ == root.local_name
    xsd_elements = [e.local_name for e in root.type.content.iter_elements()]
    assert list(model.model_fields) == xsd_elements


@pytest.mark.parametrize(
    ("topic", "xml"),
    [
        ("AOS.AOSPubDataSV.AOSDataPacket", AOS_DATA_PACKET_XML),
        ("deveny.loisTelemetry", DEVENY_TELEMETRY_XML),
        ("instrumentCube.loisTelemetry", INSTRUMENT_CUBE_XML),
        ("tcs.loisTelemetry", TCS_TELEMETRY_XML),
        ("tcs.loisTelemetry", TCS_TELEMETRY_XML_MINIMAL),
        ("WRS.WRSPubDataSV.WRSDataPacket", WRS_DATA_PACKET_XML),
    ],
)
def test_fixture_valid_against_xsd(topic, xml):
    schema(topic).validate(xml)


@pytest.mark.parametrize(
    "topic",
    [t for t, _ in SAMPLE_MODELS if (SCHEMAS / f"{t}.xsd").exists() and t != "tcs.loisTelemetry"],
)
def test_ligmos_sample_valid_against_xsd(topic):
    schema(topic).validate((SAMPLES / f"{topic}.xml").read_bytes())


@pytest.mark.xfail(strict=True, reason="ligmos sample has UNKNOWN in decimal MountDomeAzimuthDifference")
def test_ligmos_tcs_sample_valid_against_xsd():
    schema("tcs.loisTelemetry").validate((SAMPLES / "tcs.loisTelemetry.xml").read_bytes())


# ---------------------------------------------------------------------------
# InboundXmlModel leniency
# ---------------------------------------------------------------------------


def test_unknown_in_numeric_field_is_none():
    t = TcsTelemetry.from_xml(
        "<TCSTelemetry><MountDomeAzimuthDifference>UNKNOWN</MountDomeAzimuthDifference>"
        "<InPosition>unknown</InPosition><MountTemperature></MountTemperature></TCSTelemetry>"
    )
    assert t.MountDomeAzimuthDifference is None
    assert t.InPosition is None
    assert t.MountTemperature is None


def test_unknown_in_str_field_is_kept():
    t = TcsTelemetry.from_xml("<TCSTelemetry><CLSLowBankState>UNKNOWN</CLSLowBankState></TCSTelemetry>")
    assert t.CLSLowBankState == "UNKNOWN"


def test_literal_matched_case_insensitively():
    t = TcsTelemetry.from_xml(
        "<TCSTelemetry><m1CoverState>OPEN</m1CoverState><TCSState>enabled</TCSState></TCSTelemetry>"
    )
    assert t.m1CoverState == "Open"
    assert t.TCSState == "ENABLED"


def test_unknown_placeholder_in_literal_field_is_none():
    t = TcsTelemetry.from_xml("<TCSTelemetry><TCSState>UNKNOWN</TCSState></TCSTelemetry>")
    assert t.TCSState is None


def test_unexpected_literal_value_still_rejected():
    with pytest.raises(ValueError):
        TcsTelemetry.from_xml("<TCSTelemetry><TCSState>BOGUS</TCSState></TCSTelemetry>")


def test_nested_models_are_lenient():
    assert issubclass(TcsStatus, InboundXmlModel)
    a = AosDataPacket.from_xml(
        "<AOSDataPacket><tipTiltPistonDemandM1><Piston_m>UNKNOWN</Piston_m>"
        "</tipTiltPistonDemandM1></AOSDataPacket>"
    )
    assert a.tipTiltPistonDemandM1 is not None
    assert a.tipTiltPistonDemandM1.Piston_m is None
