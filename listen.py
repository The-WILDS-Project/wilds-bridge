"""
Smoke-test listener: connect to tanagra and print parsed model output.
Run with:  python listen.py
Stop with: Ctrl+C
"""

import asyncio
import logging

from wilds.bridge.broker import LDTBroker
from wilds.bridge.config import TOPIC_TCS_COMMAND_REPLY, TOPIC_TCS_STATUS, BrokerConfig
from wilds.bridge.models.tcs_status import TcsStatus

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("wilds.bridge").setLevel(logging.DEBUG)


async def main() -> None:
    cfg = BrokerConfig(subscriptions=[TOPIC_TCS_STATUS, TOPIC_TCS_COMMAND_REPLY])
    broker = LDTBroker(config=cfg)

    @broker.on(TOPIC_TCS_STATUS)
    async def on_status(msg: TcsStatus) -> None:
        pp = msg.pointingPositions
        t = msg.currentTimes
        print(
            f"[TCSTcsStatusSV] v={msg.tcsVersion} hb={msg.heartbeat}"
            f"  health={msg.tcsHealth}  state={msg.tcsState}"
            f"  inPos={msg.inPositionIsTrue}  mode={msg.mountGuideMode}"
        )
        if pp:
            az = pp.currentAzEl.azimuth
            el = pp.currentAzEl.elevation
            print(
                f"  target={pp.targetName}  parAngle={pp.currentParAngle:.2f}"
                f"  Az={az.degreesArc}°{az.minutesArc}'{az.secondsArc}\""
                f"  El={el.degreesAlt}°{el.minutesArc}'{el.secondsArc}\""
            )
        if t and t.lst:
            print(f"  LST={t.lst.hours}h{t.lst.minutesTime}m{t.lst.secondsTime}s  UTC={t.time}")

    @broker.on(TOPIC_TCS_COMMAND_REPLY)
    async def on_reply(raw) -> None:
        snippet = raw[:300].replace("\n", " ") if isinstance(raw, str) else repr(raw)
        print(f"[TCSTcsCommandResponseSV]  {snippet}")

    print(f"Connecting to {cfg.host}:{cfg.port} …")
    await broker.start()
    print("Connected. Listening — press Ctrl+C to stop.\n")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await broker.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
