import os
import shlex
import subprocess
from dataclasses import asdict, dataclass
from datetime import timedelta
from pathlib import Path

from stdl.dt import Timer

from tasker.notifier import Channel, Event
from tasker.task import Task

HOME = str(Path.home())
POPEN_ERROR = (
    BrokenPipeError,
    UnicodeDecodeError,
    PermissionError,
    FileNotFoundError,
)


@dataclass(frozen=True)
class CommandLineResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    time_taken: timedelta

    @property
    def dict(self):
        return asdict(self)

    @property
    def has_succeded(self):
        return self.exit_code == 0


class CommandLineTask(Task):
    def __init__(
        self,
        command: str | list[str],
        directory: str = HOME,
        name: str | None = None,
        description: str = "",
        timeout: float | None = None,
        notification_channels: list[Channel] | None = None,
        verbose: bool = True,
        stdout: bool = False,
    ) -> None:
        super().__init__(name, description, timeout, notification_channels, verbose)
        self.directory = directory
        self.stdout = stdout

        if isinstance(command, str):
            self.command: list = shlex.split(command)
        else:
            self.command: list = command

    @property
    def dict(self):
        return {
            "command": self.command,
            "directory": self.directory,
            "name": self.name,
            "description": self.description,
            "timeout": self.timeout,
            "notification_channels": [i.dict for i in self.notification_channels],
            "verbose": self.verbose,
            "stdout": self.stdout,
        }

    @property
    def _start_notification_data(self):
        data = super()._start_notification_data
        if self.verbose:
            data["directory"] = self.directory
            data["command"] = self.command_str()
        return data

    def _send_task_result_notification(self, result: CommandLineResult):
        event = Event.SUCCESS if result.has_succeded else Event.FAIL
        data = {"exit code": result.exit_code, "time taken": result.time_taken}

        if result.timed_out:
            data["timed out"] = True

        sections = {}
        if self.stdout and result.stdout:
            sections["stdout"] = result.stdout
        if not result.has_succeded and result.stderr:
            sections["stderr"] = result.stderr

        self.notifier.send_notification(event, data, sections)

    def exec(self):
        self.notifier.send_notification(Event.START, self._start_notification_data, {})

        cwd = os.getcwd()
        os.chdir(self.directory)

        timer = Timer()
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                timed_out = False
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                timed_out = True
                time_taken = timedelta(seconds=self.timeout)  # type: ignore

            exit_code = process.wait()
            time_taken = timer.stop().total
            stdout = stdout.decode()
            stderr = stderr.decode()

            result = CommandLineResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                timed_out=timed_out,
                time_taken=time_taken,
            )
        except POPEN_ERROR as e:
            result = CommandLineResult(
                exit_code=127,
                stdout="",
                stderr=str(e),
                timed_out=False,
                time_taken=timer.stop().total,
            )
        finally:
            os.chdir(cwd)

        self._send_task_result_notification(result=result)

        return result

    def command_str(self):
        return " ".join(self.command)
