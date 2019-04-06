from discord.ext import commands
import discord
from cogs.player import Player
import config
import asyncpg
import time
import aiohttp
import datetime


def get_prefix(bot, message):
    prefixes = ['g! ', 'G! ', 'greed ']
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_extensions = ['cogs.tools',
                      'cogs.greed',
                      'cogs.owner']

bot = commands.Bot(command_prefix=get_prefix)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    bot.session = aiohttp.ClientSession()
    print(f'{bot.user.name} - {bot.user.id}\nTotal Guilds: {len(bot.guilds)}\nTotal users: {len(set(bot.get_all_members()))}')


@bot.event
async def on_message(m):
    if m.author.bot:
        return
    if m.content.startswith(tuple(await bot.get_prefix(m))):
        conn = await asyncpg.connect(**config.connection)
        await conn.execute(f"INSERT INTO players (id, money, book) VALUES ({m.author.id}, 0, '[]') ON CONFLICT (id) DO NOTHING")
        bot.player = Player(*list(await conn.fetchrow(f"SELECT * FROM players WHERE id = {m.author.id}")))
        await conn.close()
    await bot.process_commands(m)


bot.run(config.token, bot=True, reconnect=True)
