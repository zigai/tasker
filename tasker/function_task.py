import signal
from contextlib import contextmanager
from typing import Any, Callable

from stdl.dt import Timer

from tasker.notifier import Channel, Event
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
        args_func: Callable[[], tuple[tuple[Any], dict[str, Any]]] | None = None,
        timeout: float | None = None,
        notification_channels: list[Channel] | None = None,
        name: str | None = None,
        description: str = "",
        show_result: bool = False,
        result_serializer=str,
        verbose: bool = True,
    ) -> None:
        super().__init__(name, description, timeout, notification_channels, verbose)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.show_result = show_result
        self.result_serializer = result_serializer
        self.args_func = args_func

    def exec(self):
        self.notifier.send_notification(Event.START, self._start_notification_data, {})

        result_data = {}
        timer = Timer()
        notification_event = Event.SUCCESS
        if self.timeout is None:
            try:
                if self.args_func:
                    self.args, self.kwargs = self.args_func()
                result = self.function(*self.args, **self.kwargs)
            except Exception as e:
                result = None
                notification_event = Event.FAIL
                result_data["exception"] = str(e)
        else:
            try:
                with timeout(self.timeout):
                    result = self.function(*self.args, **self.kwargs)
            except TimeoutError as e:
                result = None
                result_data["timed out"] = True
                notification_event = Event.FAIL
            except Exception as e:
                result = None
                notification_event = Event.FAIL
                result_data["exception"] = str(e)

        time_taken = timer.stop().total

        sections = {}
        result_data["time taken"] = time_taken
        if self.show_result:
            sections["result"] = self.result_serializer(result)
        self.notifier.send_notification(notification_event, result_data, sections)

        return result

    @property
    def _start_notification_data(self):
        data = super()._start_notification_data
        if self.verbose:
            if self.args:
                data["args"] = self.args
            if self.kwargs:
                data["kwargs"] = self.kwargs
        return data


__all__ = [
    "TimeoutError",
    "timeout",
    "FunctionTask",
]
