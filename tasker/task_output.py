from dataclasses import dataclass


@dataclass()
class TaskOutput:
    exit_code: int
    std_out: str
    std_err: str
    timed_out: bool