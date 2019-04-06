from discord.ext import commands
import discord
from cogs.player import Player
import config
import asyncpg
import time
import aiohttp
import datetime
bot = commands.Bot(command_prefix=['g! ', 'G! ', 'greed '])


# ==================================================LOAD-FUNCTIONS======================================================


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


# ===================================================GAME-COMMANDS======================================================


@bot.command(case_insensitive=True)
async def info(ctx):
    """Shows how many players have are inside Greed Island."""
    conn = await asyncpg.connect(**config.connection)
    players = list(await conn.fetchrow('SELECT COUNT(id) FROM players'))[0]
    await conn.close()
    await ctx.send(f"Currently there are {players} players on the island from {len(bot.guilds)} different servers!")


@bot.command(case_insensitive=True)
async def stats(ctx):
    """Displays how much money you currently have available"""
    await ctx.send(f'You have a total of {ctx.bot.player.wallet} jenny.')


# ===================================================TOOL-COMMANDS======================================================


@bot.command()
async def ping(ctx):
    """Pong! - Returns latencies."""
    typing_s = time.monotonic()
    await ctx.trigger_typing()
    typing_e = time.monotonic()
    typing_ms = round((typing_e-typing_s)*1000)
    latency_ms = round(bot.latency*1000)
    discord_s = time.monotonic()
    async with bot.session.get("https://discordapp.com/") as response:
        if response.status is 200:
            discord_e = time.monotonic()
            discord_ms = round((discord_e-discord_s)*1000)
            average = round((typing_ms+latency_ms+discord_ms)/3)
            discord_ms = f"{discord_ms}ms"
        else:
            discord_ms = "Failed"
            average = round((typing_ms + latency_ms) / 2)
    embed = discord.Embed(title="🏓 PONG", colour=discord.Colour(0x0080ff))
    embed.add_field(name="Typing:", value=f"{typing_ms}ms")
    embed.add_field(name="Latency:", value=f"{latency_ms}ms")
    embed.add_field(name="Discord:", value=f"{discord_ms}")
    embed.set_footer(text=f"Average: {average}ms")
    await ctx.send(embed=embed)


@bot.command()
async def up(ctx):
    """Displays time since last reboot."""
    t, order, = {}, ['days', 'hours', 'minutes', 'seconds']
    total_time = (datetime.datetime.now() - bot.start_time).seconds
    t[order[1]], remainder = divmod(int(total_time), 3600)
    t[order[2]], t[order[3]] = divmod(remainder, 60)
    t[order[0]], t[order[1]] = divmod(t[order[1]], 24)
    timestamp = [str(t[o])+' '+str(o) for o in order if t[o] != 0]
    timestamp = [stamp.strip('s') if stamp.startswith('1 ') else stamp for stamp in timestamp]
    await ctx.send(f"Time since last reboot: {' '.join(timestamp)}")




bot.run(config.token)
