"""
Unit tests for Telescope.set_rotator().

Uses a stub broker that records sent commands — no STOMP connection needed.
"""

import pytest

from wilds.bridge.models.tcs_command import TcsNewScienceTarget, TcsScienceTargetCommand
from wilds.bridge.models.tcs_status import TcsStatus
from wilds.bridge.store import TelemetryStore
from wilds.bridge.telescope import TargetUnknownError, Telescope

from .fixtures import NEW_SCIENCE_TARGET_XML, TCS_STATUS_XML


class _StubBroker:
    def __init__(self) -> None:
        self.store = TelemetryStore()
        self.sent: list[object] = []

    async def send_tcs_command(self, command: object) -> None:
        self.sent.append(command)


@pytest.fixture
def broker():
    return _StubBroker()


@pytest.fixture
def telescope(broker):
    return Telescope(broker)  # type: ignore[arg-type]


async def test_sends_current_target_with_new_rotator(broker, telescope):
    broker.store.new_science_target = TcsNewScienceTarget.from_xml(NEW_SCIENCE_TARGET_XML)
    await telescope.set_rotator(75.0)
    [cmd] = broker.sent
    assert isinstance(cmd, TcsScienceTargetCommand)
    assert cmd.rotator.rotPA == pytest.approx(75.0)
    assert cmd.rotator.rotatorFrame == "Target"
    assert cmd.target.targetName == "Crab Nebula"


async def test_frame_override(broker, telescope):
    broker.store.new_science_target = TcsNewScienceTarget.from_xml(NEW_SCIENCE_TARGET_XML)
    await telescope.set_rotator(75.0, rot_frame="Fixed")
    assert broker.sent[0].rotator.rotatorFrame == "Fixed"


async def test_matching_status_target_allowed(broker, telescope):
    # TCS_STATUS_XML's pointing target is also "Crab Nebula".
    broker.store.new_science_target = TcsNewScienceTarget.from_xml(NEW_SCIENCE_TARGET_XML)
    broker.store.tcs_status = TcsStatus.from_xml(TCS_STATUS_XML)
    await telescope.set_rotator(75.0)
    assert len(broker.sent) == 1


async def test_refuses_without_target_report(broker, telescope):
    with pytest.raises(TargetUnknownError):
        await telescope.set_rotator(75.0)
    assert broker.sent == []


async def test_refuses_when_report_names_another_target(broker, telescope):
    broker.store.new_science_target = TcsNewScienceTarget.from_xml(
        NEW_SCIENCE_TARGET_XML.replace("Crab Nebula", "M31")
    )
    broker.store.tcs_status = TcsStatus.from_xml(TCS_STATUS_XML)
    with pytest.raises(TargetUnknownError, match="M31"):
        await telescope.set_rotator(75.0)
    assert broker.sent == []
