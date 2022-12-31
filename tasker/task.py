from __future__ import annotations

import json
import os
import pickle
import platform
import shlex
import subprocess
import uuid
from pathlib import Path
from socket import gethostname

import yaml
from loguru import logger as LOG
from stdl.dt import Timer

from tasker.task_output import TaskOutput
from tasker.util import discord_error_notify

HOME = str(Path.home())


class Action:
    REPEAT = "repeat"


class Task:
    TASK_EXT = (".json", ".yml", ".yaml", ".pkl", ".pickle")
    ACTIONS = ["repeat"]

    def __init__(
        self,
        command: str | list,
        directory: str = HOME,
        name: str = None,
        description: str = "",
        time_limit: float = None,
        on_completion: Task | str | Path = None,
        on_timeout: Task | str | Path = None,
        on_error: Task | str | Path = None,
        logfile_path: str = None,
        discord_webhooks: str | list = None,
        show_stdout: bool = False,
    ) -> None:

        if isinstance(name, str):
            self.name = name
        else:
            self.name = str(uuid.uuid4())

        self.directory = directory
        self.description = description
        self.time_limit = time_limit
        self.discord_webhooks = discord_webhooks
        self.log_path = logfile_path
        self.show_stdout = show_stdout

        if isinstance(command, str):
            self.command: list = shlex.split(command)
        else:
            self.command: list = command

        self.on_completion = self.__load_task(on_completion)
        self.on_timeout = self.__load_task(on_timeout)
        self.on_error = self.__load_task(on_error)

        if self.log_path:
            LOG.add(self.log_path)

        if not os.path.exists(self.directory):
            LOG.warning(f"Task directory '{self.directory}' currently doesn't exist")

    def set_on_timeout(self, task: str | Task | Path):
        self.on_timeout = self.__load_task(task)

    def set_on_completion(self, task: str | Task | Path):
        self.on_timeout = self.__load_task(task)

    def set_on_error(self, task: str | Task | Path):
        self.on_error = self.__load_task(task)

    def command_as_str(self):
        return " ".join(self.command)

    def __repr__(self) -> str:
        return f"Task({self.command_as_str()})"

    def to_str(self):
        s = f"Task '{self.name}:'\n"
        for key, val in self.dict.items():
            if val is None or not val:
                continue
            if key == "name":
                continue
            if key == "command":
                s += f"\t{key}: {self.command_as_str()}\n"
                continue
            s += f"\t{key}: {val}\n"
        return s

    def print(self):
        print(self.to_str())

    def __run(self):
        has_timed_out = False
        LOG.info(
            f"Starting task '{self.name}' on {gethostname()} ({platform.platform()}) in '{self.directory}'. Task command: '{self.command_as_str()}'"
        )
        timer = Timer()
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        try:
            stdout, stderr = process.communicate(timeout=self.time_limit)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            has_timed_out = True
            LOG.warning(f"Task '{self.name}' timed out. Time limit: {self.time_limit}")

        exit_code = process.wait()
        run_time = timer.stop()
        stdout = stdout.decode()
        stderr = stderr.decode()

        task_output = TaskOutput(
            exit_code=exit_code,
            std_out=stdout,
            std_err=stderr,
            timed_out=has_timed_out,
            run_time=run_time.total_seconds(),
        )

        LOG.info(f"Task '{self.name}' exited with code {exit_code}. Run time: {run_time}")

        if self.show_stdout:
            if len(stdout):
                LOG.info(f"Task '{self.name}' STDOUT:\n{stdout}")

        if exit_code != 0:
            LOG.error(f"Task '{self.name}' STDERR:\n {stderr}")

            if self.discord_webhooks is not None:
                self.__send_discord_notifications(task_output)
        return task_output

    def __send_discord_notifications(self, task_out: TaskOutput):
        hostname = gethostname()
        pltfrm = platform.platform()

        if isinstance(self.discord_webhooks, str):
            discord_error_notify(
                url=self.discord_webhooks,
                hostname=hostname,
                platform=pltfrm,
                task_name=self.name,
                task_output=task_out,
                command=self.command_as_str(),
            )

        elif isinstance(self.discord_webhooks, list):
            for url in self.discord_webhooks:
                discord_error_notify(
                    url=url,
                    hostname=hostname,
                    platform=pltfrm,
                    task_name=self.name,
                    task_output=task_out,
                    command=self.command_as_str(),
                )

    def run(self):
        cwd = os.getcwd()
        os.chdir(self.directory)
        task_out = self.__run()
        if task_out.exit_code == 0 and not task_out.timed_out:
            self.__handle_task(self.on_completion)
        elif task_out.timed_out:
            self.__handle_task(self.on_timeout)
        elif task_out.exit_code != 0:
            self.__handle_task(self.on_error)
        os.chdir(cwd)
        return task_out

    def print_task_chain(self, __indent: int = 0):
        print(" " * __indent + "-> " + self.command_as_str())
        if self.on_completion is not None:
            print(" " * __indent + "On completion:")
            if isinstance(self.on_completion, Task):
                self.on_completion.print_task_chain(__indent + 2)
            elif isinstance(self.on_completion, str):
                print(" " * __indent + self.on_completion)

        if self.on_error is not None:
            print(" " * __indent + "On error:")
            if isinstance(self.on_error, Task):
                self.on_error.print_task_chain(__indent + 2)
            elif isinstance(self.on_error, str):
                print(" " * __indent, self.on_error)

        if self.on_timeout is not None:
            print(" " * __indent + "On timeout:")
            if isinstance(self.on_timeout, Task):
                self.on_timeout.print_task_chain(__indent + 2)
            elif isinstance(self.on_timeout, str):
                print(" " * __indent, self.on_timeout)

    @property
    def dict(self):
        return vars(self)
        return {
            "name": self.name,
            "description": self.description,
            "directory": self.directory,
            "time_limit": self.time_limit,
            "on_completion": self.on_completion,
            "on_timeout": self.on_timeout,
            "on_error": self.on_error,
            "log_path": self.log_path,
            "discord_webhooks": self.discord_webhooks,
            "show_stdout": self.show_stdout,
        }

    @classmethod
    def from_dict(cls, d: dict):
        if "command" not in d:
            raise Exception(f"Task is missing key required argument 'command'")
        return cls(**d)

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> Task:
        if not path.endswith(cls.TASK_EXT):
            raise ValueError(f"Wrong filetype for {path}. Must be one of {cls.TASK_EXT}")
        if path.endswith(".json"):
            return cls.from_json(path)
        if path.endswith((".yml", ".yaml")):
            return cls.from_yaml(path)
        if path.endswith((".pkl", ".pickle")):
            return cls.deserialize(path)

    def save_as_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.dict, f, indent=4)

    def save_as_yaml(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.dict, f)

    @staticmethod
    def deserialize(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    def serialize(self, filepath: str):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    def __handle_task(self, task: str | Task):
        if task is None:
            return
        elif isinstance(task, Task):
            return task.run()
        elif isinstance(task, str):
            if task in self.ACTIONS:
                if task == "repeat":
                    return self.run()

    def __load_task(self, task: str | Task | Path):
        if task is None or isinstance(task, Task):
            return task
        if isinstance(task, str):
            if task in self.ACTIONS:
                return task
            return self.from_file(task)
        if isinstance(task, Path):
            return self.from_file(str(task))
        raise TypeError(f"Invalid type for Task ({type(task)})")
