import platform
import signal
from contextlib import contextmanager
from socket import gethostname
from typing import Callable

from stdl.dt import Timer

from tasker.notifier import Channel
from tasker.task import Task


class TimeoutError(Exception):
    pass


@contextmanager
def timeout(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutError(f"Timed out after {seconds}s")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class FunctionTask(Task):
    def __init__(
        self,
        function: Callable,
        args: tuple = (),
        kwargs: dict = {},
        name: str | None = None,
        description: str = "",
        timeout: float | None = None,
        notifications: list[Channel] | None = None,
    ) -> None:
        super().__init__(name, description, timeout, notifications)

        self.function = function
        self.args = args
        self.kwargs = kwargs

    def _log_start(self):
        self.notifier.notify(
            "start",
            f"args: {self.args}\nkwargs: '{self.kwargs}'",
            title=f"[STARTING] '{self.name}' on {gethostname()} ({platform.platform()})",
        )

    def exec(self):
        timer = Timer()
        timed_out = False
        if self.timeout is None:
            result = self.function(*self.args, **self.kwargs)
            run_time = timer.stop()
            return result
        else:
            try:
                with timeout(self.timeout):
                    result = self.function(*self.args, **self.kwargs)
                    run_time = timer.stop()
            except TimeoutError as e:
                timed_out = True
            except Exception as e:
                self._log_error(f"Exception: {e}")
                return None
        if timed_out:
            self._log_error(f"Timed out. Time limit: {self.timeout}")
            return None
        runtime_str = str(round(run_time.total_seconds(), 2)) + "s"
        self._log_success(f"'{self.name}' exited successfully. Run time: {runtime_str}")
        self._log_result(f"stdout:\n{result}")
        return result
