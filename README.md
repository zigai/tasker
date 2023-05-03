# Tasker
[![PyPI version](https://badge.fury.io/py/tasker-python.svg)](https://badge.fury.io/py/tasker-python)
![Supported versions](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Downloads](https://static.pepy.tech/badge/tasker-python)](https://pepy.tech/project/tasker-python)
[![license](https://img.shields.io/github/license/zigai/tasker.svg)](https://github.com/zigai/tasker/blob/main/LICENSE)

Encapsulate function calls and shell commands as tasks with scheduling (powered by [Rocketry](https://github.com/Miksus/rocketry)) and notifications (powered by [Apprise](https://github.com/caronc/apprise)).

# Installation
#### From PyPi
```
pip install tasker-python
```
#### From source
```
pip install git+https://github.com/zigai/tasker.git
```
# Example
```python
from tasker import Channel, CommandLineTask

discord_webhook = "discord://..."

task = CommandLineTask(
    name="hello-world",
    command="echo 'Hello World!'",
    notification_channels=[
        Channel(discord_webhook, events=["start", "success", "info", "fail"]), 
    ],
    stdout=True, # display stdout in notifications
)

task.exec() # run once

from tasker.scheduler import TaskScheduler, every
scheduler = TaskScheduler()
scheduler.schedule_task(task, every("10 seconds")) # run every 10 seconds
scheduler.run()

```

# License
[MIT License](https://github.com/zigai/tasker/blob/master/LICENSE)
