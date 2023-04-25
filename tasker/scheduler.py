from rocketry import Rocketry, conditions, conds
from rocketry.conditions import *
from rocketry.conds import *
from stdl.fs import rand_filename as randname

from tasker.notifier import Channel
from tasker.task import Task


class TaskScheduler:
    def __init__(self, notification_channels: list[Channel] | None = None) -> None:
        self.app = Rocketry()
        self.notification_channels = notification_channels or []
        self.tasks = {}

    def schedule_task(self, task: Task, at):
        name = randname(task.name)
        for channel in self.notification_channels:
            task.notifier.subscribe(channel)
        rocketry_task = self.app.task(at, func=task.exec, name=name)
        self.tasks[name] = rocketry_task
        return rocketry_task

    def run(self):
        self.app.run()
