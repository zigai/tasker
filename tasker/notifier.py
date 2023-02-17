import os
import platform
import shlex
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from socket import gethostname

from apprise import Apprise
from loguru import logger as log
from stdl import fs


@dataclass(frozen=True)
class Channel:
    channel: str
    events: list[str] = field(default_factory=lambda: ["info"])


class Notifier:
    EVENTS = ["start", "success", "error", "result", "info"]

    def __init__(self) -> None:
        self.notifiers: dict[str, Apprise] = {}
        for name in self.EVENTS:
            self.notifiers[name] = Apprise()

    def subscribe(self, notification: Channel):
        for name in notification.events:
            self.notifiers[name].add(notification.channel)

    def notify(self, event: str, body: str, title: str = ""):
        if event not in self.EVENTS:
            log.warning(f"Event '{event}' is not a valid event. Valid events are: {self.EVENTS}")
            return
        self.notifiers[event].notify(body=body, title=title)
