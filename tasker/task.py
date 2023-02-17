import platform
import uuid
from socket import gethostname

from stdl import fs

from tasker.notifier import Channel, Notifier


class Task:
    def __init__(
        self,
        name: str | None = None,
        description: str = "",
        timeout: float | None = None,
        notification_channels: list[Channel] | None = None,
    ) -> None:
        self._id = uuid.uuid4()
        self.description = description
        self.timeout = timeout
        self.name: str = name  # type: ignore
        if self.name is None:
            self.name = f"Task {self._id}"
        self.notifier = Notifier()
        if notification_channels is not None:
            for i in notification_channels:
                self.notifier.subscribe(i)

    def __repr__(self) -> str:
        return f"Task(name='{self.name}', id='{self._id})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Task):
            return self._id == other._id
        raise NotImplementedError

    def exec(self):
        raise NotImplementedError

    def _exec(self):
        raise NotImplementedError

    def add_notification_channel(self, channel: Channel):
        self.notifier.subscribe(channel)

    def _log_info(self, message: str):
        self.notifier.notify("info", message, title=f"[INFO] {self.name}")

    def _log_start(self):
        self.notifier.notify(
            "start",
            f"Starting '{self.name}' on {gethostname()} ({platform.platform()})",
        )

    def _log_success(self, message: str):
        self.notifier.notify("success", message, title=f"[SUCCESS] {self.name}")

    def _log_result(self, result: str):

        self.notifier.notify("result", result, title=f"[RESULT] {self.name}")

    def _log_error(self, message: str):

        self.notifier.notify("error", message, title=f"[ERROR] {self.name}")

    def save_as_json(self, path: str):
        fs.json_dump(self.dict, path, indent=4)

    def save_as_yaml(self, path: str):
        fs.yaml_dump(self.dict, path)

    @property
    def dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

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
