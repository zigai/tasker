from dataclasses import asdict, dataclass, field

from apprise import Apprise, NotifyFormat
from stdl.dt import fmt_datetime
from stdl.log import br
from stdl.str_u import colored


class Event:
    START = "start"
    SUCCESS = "success"
    FAIL = "fail"
    INFO = "info"


@dataclass(frozen=True)
class Channel:
    url: str
    events: list[str] = field(default_factory=lambda: [Event.INFO, Event.FAIL])

    @property
    def dict(self):
        return asdict(self)


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


class TextNotificationFormatter:
    format = NotifyFormat.TEXT  # type: ignore

    event_titles = {
        Event.START: colored("STARTING", "blue"),
        Event.SUCCESS: colored("SUCCESS", "green"),
        Event.FAIL: colored("FAIL", "red"),
        Event.INFO: colored("INFO", "gray"),
    }

    def __init__(self, events: list[str] | None = None, ms=True, plain: bool = False) -> None:
        self.events = events or [Event.START, Event.FAIL]
        self.plain = plain
        self.ms = ms
        if self.plain:
            self.event_titles = {
                Event.START: "STARTING",
                Event.SUCCESS: "SUCCESS",
                Event.FAIL: "FAIL",
                Event.INFO: "INFO",
            }

    def _get_title(self, name: str, event: str) -> str:
        title = f"{fmt_datetime(d_sep='/',ms=self.ms)} | task '{name}' {self.event_titles[event]}"
        return title

    def format_notification(self, name: str, event: str, data: dict, sections: dict) -> str:
        title = self._get_title(name, event)
        message = [title]
        if data:
            for key, value in data.items():
                message.append(f"  {key}: {value}")
        if sections:
            for key, value in sections.items():
                message.append(f"[-] {key}:")
                message.append(value)
        return "\n".join(message)

    def notify(self, name: str, event: str, data: dict, sections: dict) -> None:
        if not event in self.events:
            return
        message = self.format_notification(name, event, data, sections)
        print(message)
        br()


TEXT_NOTIFICATION_FORMATTER = TextNotificationFormatter()


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
        if self.console:
            TEXT_NOTIFICATION_FORMATTER.notify(
                name=self.name, event=event, data=data, sections=sections
            )

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
    "TextNotificationFormatter",
    "TEXT_NOTIFICATION_FORMATTER",
]
