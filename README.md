# Tasker
[![PyPI version](https://badge.fury.io/py/py-tasker.svg)](https://badge.fury.io/py/py-tasker)
![Supported versions](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Downloads](https://static.pepy.tech/badge/py-tasker)](https://pepy.tech/project/py-tasker)
[![license](https://img.shields.io/github/license/zigai/tasker.svg)](https://github.com/zigai/tasker/blob/main/LICENSE)

Encapsulate function calls and shell commands as tasks with scheduling (powered by [Rocketry](https://github.com/Miksus/rocketry)) and notifications (powered by [Apprise](https://github.com/caronc/apprise)).

# Installation
#### From PyPi
```
pip install py-tasker
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
scheduler.schedule_task(every("10 seconds"), task) # run every 10 seconds
scheduler.run()

```

# License
[MIT License](https://github.com/zigai/tasker/blob/master/LICENSE)
