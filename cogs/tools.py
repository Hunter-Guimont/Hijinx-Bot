import discord
from discord.ext import commands
import datetime
import time
import config
import asyncpg
import psutil


class Tools(commands.Cog):
    """some basic utils"""

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    @commands.command(case_insensitive=True)
    async def ping(self, ctx):
        """Pong! - Returns latencies."""
        typing_s = time.monotonic()
        await ctx.trigger_typing()
        typing_e = time.monotonic()
        typing_ms = round((typing_e - typing_s) * 1000)
        latency_ms = round(self.bot.latency * 1000)
        discord_s = time.monotonic()
        async with self.bot.session.get("https://discordapp.com/") as response:
            if response.status is 200:
                discord_e = time.monotonic()
                discord_ms = round((discord_e - discord_s) * 1000)
                average = round((typing_ms + latency_ms + discord_ms) / 3)
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

    @commands.command(case_insensitive=True)
    async def up(self, ctx):
        """Displays time since last reboot."""
        t, order, = {}, ['days', 'hours', 'minutes', 'seconds']
        total_time = (datetime.datetime.now() - self.bot.start_time).seconds
        t[order[1]], remainder = divmod(int(total_time), 3600)
        t[order[2]], t[order[3]] = divmod(remainder, 60)
        t[order[0]], t[order[1]] = divmod(t[order[1]], 24)
        timestamp = [str(t[o]) + ' ' + str(o) for o in order if t[o] != 0]
        timestamp = [stamp.strip('s') if stamp.startswith('1 ') else stamp for stamp in timestamp]
        await ctx.send(f"Time since last reboot: {' '.join(timestamp)}")

    @commands.command(case_insensitive=True)
    async def info(self, ctx):
        """Shows how many players have are inside Greed Island."""
        conn = await asyncpg.connect(**config.connection)
        players, guilds = list(await conn.fetchrow('SELECT COUNT(id) FROM players'))[0], len(self.bot.guilds)
        await conn.close()
        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        await ctx.send(f"Currently there are {players} players on the island from {guilds} different servers!")
        await ctx.send(f"Memory Usage: {round(memory_usage, 1)}mb. CPU Usage: {int(cpu_usage)}%.")


def setup(bot):
    bot.add_cog(Tools(bot))
