from __future__ import annotations

import os

from loguru import logger as LOG
from stdl import fs

from tasker.task import Task


class TaskManager:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def load_from_dir(self, directory: str) -> None:
        if not os.path.exists(directory):
            LOG.error(f"Directory '{directory}' does not exist")
            raise FileNotFoundError(directory)
        task_files = fs.get_files_in(directory)

        for file in task_files:
            if file.endswith(Task.TASK_EXT):
                self.add(Task.from_file(file))

    def add(self, t: Task):
        if not isinstance(t, Task):
            LOG.error("Parameter must be an instance of Task")
            raise TypeError(type(t))
        self.tasks.append(t)

    def find(self, name: str) -> Task | None:
        for task in self.tasks:
            if task.name == name:
                return task
        LOG.warning(f"Task '{name}' not found.")
        return None

    def print_tasks(self) -> None:
        for t in self.tasks:
            print(t, "\n")
