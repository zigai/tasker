import platform
from socket import gethostname


def get_device_info() -> str:
    return f"{gethostname()} ({platform.platform()}"
