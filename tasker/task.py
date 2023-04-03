from typing import Any

from stdl import fs
from stdl.fs import rand_filename as rand_name

from tasker.notifier import Channel, Notifier
from tasker.util import get_device_info


class Task:
    def __init__(
        self,
        name: str | None = None,
        description: str = "",
        timeout: float | None = None,
        notification_channels: list[Channel] | None = None,
        verbose: bool = False,
    ) -> None:
        self.description = description
        self.timeout = timeout
        self.verbose = verbose

        self.name: str = name  # type: ignore
        if self.name is None:
            self.name = rand_name("task")

        self.notifier = Notifier(name=self.name)
        self.notification_channels = notification_channels or []
        if notification_channels:
            for channel in notification_channels:
                self.notifier.subscribe(channel)

    def __repr__(self) -> str:
        return f"Task(name='{self.name}', description='{self.description}', timeout={self.timeout})"

    @property
    def dict(self):
        return vars(self)

    def add_notification_channel(self, channel: Channel):
        self.notification_channels.append(channel)
        self.notifier.subscribe(channel)

    def save_as_json(self, path: str):
        fs.json_dump(self.dict, path, indent=4)

    def save_as_yaml(self, path: str):
        fs.yaml_dump(self.dict, path)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @classmethod
    def from_json(cls, path: str):
        return cls.from_dict(fs.json_load(path))

    @classmethod
    def from_yaml(cls, path: str):
        return cls.from_dict(fs.yaml_load(path))

    @classmethod
    def from_file(cls, path: str):
        if path.endswith((".yml", ".yaml")):
            return cls.from_yaml(path)
        return cls.from_json(path)

    @property
    def _start_notification_data(self):
        data: dict[str, Any] = {"device": get_device_info()}
        if self.timeout is not None:
            data["timeout"] = self.timeout
        if self.verbose and self.description:
            data["description"] = self.description
        return data

    def exec(self):
        raise NotImplementedError


__all__ = ["Task"]
