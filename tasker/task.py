from __future__ import annotations

import json
import os
import pickle
import sys
from subprocess import PIPE, Popen, TimeoutExpired

import yaml
from loguru import logger as LOG

from tasker.task_output import TaskOutput
from tasker.utils import Timer


class Task:
    TASK_EXT = (".json", ".yml", ".yaml", ".pkl", ".pickle")
    TASK_ARGS = [
        "directory", "program", "args", "name", "time_limit", "description", "on_completion", "on_timeout", "on_error",
        "parent_name", "log_path"
    ]

    def __init__(self,
                 directory: str,
                 program: str,
                 args: str = "",
                 name: str | None = None,
                 time_limit: float | None = None,
                 description: str | None = None,
                 on_completion: Task | str | None = None,
                 on_timeout: Task | str | None = None,
                 on_error: Task | str | None = None,
                 parent_name: str | None = None,
                 log_path: str | None = None,
                 show_stdout: bool = False) -> None:
        self.directory = directory
        self.program = program
        self.name = name
        self.description = description
        self.args = args
        self.time_limit = time_limit
        self.on_completion = self.__load_task(on_completion)
        self.on_timeout = self.__load_task(on_timeout)
        self.on_error = self.__load_task(on_error)
        self.parent_name = parent_name
        self.log_path = log_path
        self.show_stdout = show_stdout
        self.cwd = os.getcwd()

        self.__apply_os_fixes()
        if self.log_path:
            LOG.add(self.log_path)
        if not os.path.exists(self.directory):
            LOG.warning(f"Task directory currently doesn't exist")

    def __repr__(self) -> str:
        return f"<Task: '{self.name}', command: '{self.get_command_full()}'>"

    def __run(self, cmd: str):
        LOG.info(f"Starting task '{self.name}' on {sys.platform} in {self.directory}")
        LOG.info(f"Command: {self.get_command()}")

        timed_out = False
        timer = Timer()
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)

        try:
            stdout, stderr = process.communicate(timeout=self.time_limit)
        except TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            timed_out = True
            LOG.warning(f"Task '{self.name}'timed out. Time limit: {self.time_limit}")
        exit_code = process.wait()
        runtime = timer.stop()

        LOG.info(f"Task '{self.name}' exited with code {exit_code}. Runtime: {runtime}")

        if self.show_stdout:
            LOG.info(f"Output:\n{stdout.decode()}")

        if exit_code != 0:
            LOG.info(f"Error message:\n {stderr.decode()}")
        return TaskOutput(exit_code, stdout.decode(), stderr.decode(), timed_out)

    def run(self):
        os.chdir(self.directory)
        command = self.get_command()
        r = self.__run(command)

        if r.exit_code == 0 and not r.timed_out:
            if self.on_completion:
                self.on_completion.run()

        if r.timed_out:
            if self.on_timeout:
                self.on_timeout.run()

        if r.exit_code != 0:
            if self.on_error:
                self.on_error.run()
        os.chdir(self.cwd)
        return r

    def get_command(self):
        return f"{self.program} {self.args}"

    def get_command_full(self):
        return f"{self.directory} {self.get_command()}"

    def to_str(self):
        task = self.to_dict()
        s = f"Task '{self.name}:'\n"
        for key, val in task.items():
            if val is None:
                continue
            if key == "name":
                continue
            s += f"\t{key}: {val}\n"
        return s

    def print(self):
        print(self.to_str())

    def print_task_chain(self, __indent: int = 0):
        print(" " * __indent + "-> " + self.get_command_full())
        if self.on_completion:
            self.on_completion.print_task_chain(__indent + 2)

    def to_dict(self):
        d = {
            "directory": self.directory,
            "program": self.program,
            "args": self.args,
            "name": self.name,
            "time_limit": self.time_limit,
            "description": self.description,
            "on_completion": self.on_completion,
            "on_timeout": self.on_timeout,
            "on_error": self.on_error,
            "parent_name": self.parent_name,
            "log_path": self.log_path,
            "show_stdout": self.show_stdout
        }
        return d

    @staticmethod
    def from_dict(d: dict):
        for key in Task.TASK_ARGS:
            if key not in d:
                LOG.error(f"Task is missing key '{key}'")
                raise Exception(f"Task is missing key '{key}'")
        """
        return Task(directory=d["directory"],
                    program=d["program"],
                    args=d["args"],
                    name=d["name"],
                    time_limit=float(d["time_limit"]),
                    description=d["description"],
                    on_completion=d["on_completion"],
                    on_timeout=d["on_timeout"],
                    on_error=d["on_error"],
                    parent_name=d["parent_name"],
                    log_path=d["log_path"])
        """
        return Task(**d)

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
        if path.endswith(".json"):
            return cls.from_json(path)
        if path.endswith((".yml", ".yaml")):
            return cls.from_yaml(path)
        if path.endswith((".pkl", ".pickle")):
            return cls.from_json(path)
        LOG.warning(f"File Extension for file '{path}' not recognized. Attempting to deserialize file.")
        return cls.deserialize(path)

    def save_as_json(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def save_as_yaml(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.to_dict(), f)

    def deserialize(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    def serialize(self, filepath: str):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    def __apply_os_fixes(self):
        if sys.platform == "linux":
            if self.program == "python":
                self.program = "python3"
        if sys.platform == "win32":
            if self.program == "python3":
                self.program = "python"

    def __load_task(self, t: str | Task | None):
        if t is None or isinstance(t, Task):
            return t
        if isinstance(t, str):
            return self.from_file(t)

def cli():
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print("Usage:")
        print(f"\t{sys.argv[0]} run <path>")
        print(f"\t{sys.argv[0]} new <path>")
        exit(0)

    if sys.argv[1] == "run":
        task = Task.from_file(sys.argv[2])
        task.print()
        task.run()

    if sys.argv[1] == "new":
        t = """args:
program:
directory:
name:
description:
log_path:
on_completion:
on_error:
on_timeout:
parent_name:
time_limit:"""
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(t)

if __name__ == '__main__':
    cli()
