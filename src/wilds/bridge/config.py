from dataclasses import dataclass, field

# ActiveMQ topic names — subscribe (status/telemetry)
TOPIC_TCS_TELEMETRY = "tcs.loisTelemetry"
TOPIC_TCS_STATUS = "TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV"
TOPIC_WRS_TELEMETRY = "wrs.loisTelemetry"
TOPIC_WRS_DATA_PACKET = "WRS.WRSPubDataSV.WRSDataPacket"
TOPIC_AOS_TELEMETRY = "aos.loisTelemetry"
TOPIC_AOS_DATA_PACKET = "AOS.AOSPubDataSV.AOSDataPacket"
TOPIC_INSTRUMENT_CUBE = "instrumentCube.loisTelemetry"
TOPIC_WILDS_TELEMETRY = "wilds.loisTelemetry"

# ActiveMQ topic names — publish (commands)
TOPIC_TCS_COMMAND = "TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV"
TOPIC_TCS_COMMAND_REPLY = "TCS.TCSSharedVariables.TCSLowLevelStatusSV.TCSTcsCommandResponseSV"
TOPIC_NEW_SCIENCE_TARGET = "TCS.TCSSharedVariables.TCSLowLevelStatusSV.NewScienceTargetSV"
TOPIC_AOS_FOCUS_ABSOLUTE = "AOS.AOSSubDataSV.AbsoluteFocusOffset"   # float in meters
TOPIC_AOS_FOCUS_RELATIVE = "AOS.AOSSubDataSV.RelativeFocusOffset"   # float in meters
TOPIC_AOS_FOCUS_CLEAR = "AOS.AOSSubDataSV.ClearFocusOffset"         # send "true"

# Topics the bridge subscribes to by default
DEFAULT_SUBSCRIPTIONS = [
    TOPIC_TCS_TELEMETRY,
    TOPIC_TCS_STATUS,
    TOPIC_WRS_DATA_PACKET,
    TOPIC_AOS_DATA_PACKET,
    TOPIC_INSTRUMENT_CUBE,
]


@dataclass
class BrokerConfig:
    # "tanagra.lowell.edu" for Mars Hill test; "joe" for production
    host: str = "tanagra.lowell.edu"
    port: int = 61613
    username: str = "admin"
    password: str = "admin"

    # Seconds to wait before reconnecting after a dropped connection
    reconnect_sleep: float = 5.0

    # Topics to subscribe to on connect
    subscriptions: list[str] = field(default_factory=lambda: list(DEFAULT_SUBSCRIPTIONS))

    # How many recent message hashes to keep per topic for JOE duplicate detection
    dedup_cache_size: int = 4
