from dataclasses import dataclass, field


# ActiveMQ topic names
TOPIC_TCS_TELEMETRY = "tcs.loisTelemetry"
TOPIC_TCS_STATUS = "TCS.TCSSharedVariables.TCSHighLevelStatusSV.TCSTcsStatusSV"
TOPIC_WRS_TELEMETRY = "wrs.loisTelemetry"
TOPIC_AOS_TELEMETRY = "aos.loisTelemetry"
TOPIC_WILDS_TELEMETRY = "wilds.loisTelemetry"
TOPIC_TCS_COMMAND = "TCS.TCSSharedVariables.TCSSubData.TCSTcsCommandSV"
TOPIC_TCS_COMMAND_REPLY = "TCS.TCSSharedVariables.TCSLowLevelStatusSV.TCSTcsCommandResponseSV"

# Topics the bridge subscribes to by default
DEFAULT_SUBSCRIPTIONS = [
    TOPIC_TCS_TELEMETRY,
    TOPIC_TCS_STATUS,
    TOPIC_WRS_TELEMETRY,
    TOPIC_AOS_TELEMETRY,
]


@dataclass
class BrokerConfig:
    # "lo-webrat.lowell.edu" for test; "joe" for production
    host: str = "lo-webrat.lowell.edu"
    port: int = 61613
    username: str = "admin"
    password: str = "admin"

    # Seconds to wait before reconnecting after a dropped connection
    reconnect_sleep: float = 5.0

    # Topics to subscribe to on connect
    subscriptions: list[str] = field(default_factory=lambda: list(DEFAULT_SUBSCRIPTIONS))

    # How many recent message hashes to keep per topic for JOE duplicate detection
    dedup_cache_size: int = 4
