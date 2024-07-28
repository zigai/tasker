# Tasker
[![PyPI version](https://badge.fury.io/py/tasker-python.svg)](https://badge.fury.io/py/tasker-python)
![Supported versions](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Downloads](https://static.pepy.tech/badge/tasker-python)](https://pepy.tech/project/tasker-python)
[![license](https://img.shields.io/github/license/zigai/tasker.svg)](https://github.com/zigai/tasker/blob/main/LICENSE)

Simple task automation framework for Python, integrating [Rocketry](https://github.com/Miksus/rocketry) for advanced scheduling and [Apprise](https://github.com/caronc/apprise) for multi-platform notifications. Wraps Python functions and shell commands into easily manageable and schedulable units.

## Installation
#### From PyPi
```
pip install tasker-python
```
#### From source
```
pip install git+https://github.com/zigai/tasker.git
```
## Example
```python
from tasker import Channel, CommandLineTask

task = CommandLineTask(
    name="hello-world",
    command="echo 'Hello World!'",
    notification_channels=[
        Channel("discord://...", events=["start", "success", "info", "fail"]), 
    ],
    stdout=True, # display stdout in notifications
)

task.exec() # run once

from tasker.scheduler import TaskScheduler, every
scheduler = TaskScheduler()
scheduler.schedule_task(task, every("10 seconds")) # run every 10 seconds
scheduler.run()

```

## License
[MIT License](https://github.com/zigai/tasker/blob/master/LICENSE)
