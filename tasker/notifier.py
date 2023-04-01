import sys
from dataclasses import dataclass, field

from apprise import Apprise, NotifyFormat
from stdl.dt import fmt_datetime


class Event:
    START = "start"
    SUCCESS = "success"
    FAIL = "fail"
    INFO = "info"


@dataclass(frozen=True)
class Channel:
    url: str
    events: list[str] = field(default_factory=lambda: [Event.INFO, Event.FAIL])


class MarkdownNotificationFormatter:
    format = NotifyFormat.MARKDOWN  # type: ignore
    min_ljust = 10
    max_ljust = 20

    event_titles = {
        Event.START: "STARTING",
        Event.SUCCESS: "SUCCESS",
        Event.FAIL: "FAIL",
        Event.INFO: "INFO",
    }

    event_emojis = {
        Event.START: ":blue_circle:",
        Event.SUCCESS: ":green_circle:",
        Event.FAIL: ":red_circle:",
        Event.INFO: ":white_circle:",
    }

    def __init__(self, ms=True) -> None:
        self.ms = ms

    def _get_title(self, name: str, event: str) -> str:
        title = f"{self.event_emojis[event]} `{fmt_datetime(d_sep='/',ms=self.ms)}`  **|**  task  `{name}` {self.event_titles[event]}"
        return title

    def format_notification(self, name: str, event: str, data: dict, sections: dict) -> str:
        title = self._get_title(name, event)
        if data:
            body = ">>> "
            for key, value in data.items():
                body += f"{key}: `{value}`\n"
        else:
            body = ""
        if sections:
            body += "\n"
            for key, value in sections.items():
                body += f"**{key}**\n```{value}```\n"
        return title + " \n" + body


class Notifier:
    EVENTS = ["start", "success", "fail", "info"]

    def __init__(
        self, name: str, fmt_class=MarkdownNotificationFormatter, console: bool = True
    ) -> None:
        self.name = name
        self.formatter = fmt_class()
        self.console = console
        self.notifiers: dict[str, Apprise] = {}
        for event in self.EVENTS:
            self.notifiers[event] = Apprise()

    def subscribe(self, channel: Channel):
        for event in channel.events:
            self._validate_event(event)
            self.notifiers[event].add(channel.url)

    def send_notification(self, event: str, data: dict, sections: dict):
        self._validate_event(event)
        body = self.formatter.format_notification(
            name=self.name, event=event, data=data, sections=sections
        )
        self.notifiers[event].notify(body=body, body_format=self.formatter.format)

    def _validate_event(self, event: str):
        if event not in self.EVENTS:
            raise ValueError(
                f"'{event}' is not a valid event. Valid options are: {', '.join(self.EVENTS)}"
            )


__all__ = [
    "Event",
    "Channel",
    "MarkdownNotificationFormatter",
    "Notifier",
]
