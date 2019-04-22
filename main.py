import datetime

import discord
from discord.ext import commands

import config


def get_prefix(bot_, message):
    prefixes = ['*', 'h!']
    return commands.when_mentioned_or(*prefixes)(bot_, message)


bot = commands.Bot(command_prefix=get_prefix, owner_id=222800179697287168)

initial_extensions = ['cogs.stats',
                      'cogs.admin',
                      # 'cogs.pokemon',
                      'cogs.api',
                      'cogs.fun',
                      # 'cogs.help',
                      'cogs.handler']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    activity = discord.Activity(name="*help and h!help.", type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)
    print(
        f'{bot.user.name} - {bot.user.id}\n'
        f'Total Guilds: {len(bot.guilds)}\n'
        f'Total users: {len(set(bot.get_all_members()))}'
    )


bot.run(config.token, bot=True, reconnect=True)
