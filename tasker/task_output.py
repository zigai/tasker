from dataclasses import asdict, dataclass


@dataclass()
class TaskOutput:
    exit_code: int
    std_out: str
    std_err: str
    run_time: float
    timed_out: bool

    @property
    def dict(self):
        return asdict(self)
