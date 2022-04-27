import platform
from datetime import timedelta
from os import sep, walk
from socket import gethostname
from time import time

from discord_webhook import DiscordEmbed, DiscordWebhook


class Timer:

    def __init__(self):
        self.start_time = time()

    def stop(self):
        run_time = timedelta(seconds=time() - self.start_time)
        return run_time


def get_files_in(directory: str):
    f = []
    for subdir, _, files in walk(directory):
        for file in files:
            filepath = subdir + sep + file
            f.append(filepath)
    return f


def discord_webhook_msg(url: str, content: str):
    webhook = DiscordWebhook(url=url, rate_limit_retry=True, content=content)
    response = webhook.execute()
    return response


def discord_webhook_err_msg(url: str, content: str, stderr: str):
    webhook = DiscordWebhook(url=url, rate_limit_retry=True, content=content)
    embed = DiscordEmbed(title=content, description=stderr, color='03b2f8')
    webhook.add_embed(embed)
    response = webhook.execute()
    return response


def get_device_info():
    return f"{gethostname()} - {platform.platform()}"
