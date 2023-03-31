import os
import platform
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from socket import gethostname

from loguru import logger as log
from stdl import fs
from stdl.dt import Timer

from tasker.notifier import Channel
from tasker.task import Task

HOME = str(Path.home())


@dataclass()
class ShellOutput:
    exit_code: int
    std_out: str
    std_err: str
    run_time: float
    timed_out: bool

    @property
    def dict(self):
        return asdict(self)


class ShellTask(Task):
    def __init__(
        self,
        command: str | list[str],
        directory: str = HOME,
        name: str | None = None,
        description: str = "",
        timeout: float | None = None,
        notifications: list[Channel] | None = None,
    ) -> None:
        super().__init__(name, description, timeout, notifications)
        self.directory = directory
        if isinstance(command, str):
            self.command: list = shlex.split(command)
        else:
            self.command: list = command
        if not os.path.exists(self.directory):
            log.warning(f"Directory '{self.directory}' currently doesn't exist")

    def _log_start(self):
        self.notifier.notify(
            "start",
            f"Command: '{self.command_str()}'",
            title=f"[STARTING] '{self.name}' on {gethostname()} ({platform.platform()})",
        )

    def exec(self):
        cwd = os.getcwd()
        os.chdir(self.directory)
        task_out = self._exec()
        os.chdir(cwd)
        return task_out

    def _exec(self):
        timed_out = False
        self._log_start()
        timer = Timer()
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            timed_out = True
            self._log_error(f"Timed out. Time limit: {self.timeout}")

        exit_code = process.wait()
        run_time = timer.stop()
        stdout = stdout.decode()
        stderr = stderr.decode()

        output = ShellOutput(
            exit_code=exit_code,
            std_out=stdout,
            std_err=stderr,
            timed_out=timed_out,
            run_time=run_time.total_seconds(),
        )

        self._log_result(f"stdout:\n{stdout}")

        runtime_str = str(round(output.run_time, 2)) + "s"
        if exit_code != 0:
            message = f"Exited with code {exit_code}.\n Run time: {runtime_str}"
            message += f"\n Command: '{self.command_str()}'"
            message += f"\n stderr:\n{stderr}"
            self._log_error(message)
        else:
            self._log_success(f"'{self.name}' exited successfully. Run time: {runtime_str}")
        return output

    def command_str(self):
        return " ".join(self.command)
