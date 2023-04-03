from rocketry import Rocketry, conditions, conds
from rocketry.conditions import *
from rocketry.conds import *
from stdl.fs import rand_filename as randname

from tasker import Task
from tasker.notifier import Channel


class TaskScheduler:
    def __init__(self, notification_channels: list[Channel] | None = None) -> None:
        self.app = Rocketry()
        self.notification_channels = notification_channels or []

    def schedule_task(self, at, task: Task):
        name = randname(task.name)
        for channel in self.notification_channels:
            task.notifier.subscribe(channel)
        self.app.task(at, func=task.exec, name=name)

    def run(self):
        self.app.run()
