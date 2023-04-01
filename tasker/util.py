import platform
from socket import gethostname


def get_device_info():
    return f"{gethostname()} ({platform.platform()}"
