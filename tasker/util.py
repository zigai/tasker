from datetime import timedelta
from os import sep, walk
from time import time

from discord_webhook import DiscordEmbed, DiscordWebhook

from tasker.task_output import TaskOutput


def discord_error_notify(url: str, task_name: str, task_output: TaskOutput, platform: str,
                         hostname: str, command: str):
    title = f"Task '{task_name}' exited with code {task_output.exit_code}"
    webhook = DiscordWebhook(url=url, rate_limit_retry=True)
    embed = DiscordEmbed(title=title, description=task_output.std_err, color='03b2f8')
    embed.add_embed_field(name='Command', value=command, inline=False)
    embed.add_embed_field(
        name='Runtime',
        value=str(round(task_output.run_time, 2)) + "s",
        inline=False,
    )
    embed.add_embed_field(name='Hostname', value=hostname, inline=False)
    embed.add_embed_field(name='Platform', value=platform, inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()
    return response
