import datetime
from os import walk
from os.path import join

import discord
import humanfriendly
import psutil
from discord.ext import commands


class Stats(commands.Cog):
    """Current bot statistics."""

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    def get_uptime(self, *, brief=False):
        now = datetime.datetime.now()
        then = self.bot.start_time
        delta = round((now - then).total_seconds())
        time = humanfriendly.format_timespan(delta)
        if brief:
            time = time.replace(',', '').replace('and', '')
            time = time.split()
            words = [item[0] + ' ' if item.isalpha() else item for item in time]
            time = ''.join(words)
        return time

    @staticmethod
    def get_lines():
        py = []
        for root, dirs, files in walk("."):
            py += [join(root, file) for file in files if file.endswith('.py')]

        lines = 0
        for file in py:
            with open(file) as f:
                lines += len([line for line in f if not line.startswith('#') or line == ''])

        return lines, len(py)

    @commands.command()
    async def uptime(self, ctx):
        """Displays time since bot went online"""

        desc = f"**✈️ {self.get_uptime()}.**"

        embed = discord.Embed(description=desc)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Displays bots latency."""

        desc = f"**🏓 {round(self.bot.latency * 1000)}ms**"

        embed = discord.Embed(description=desc)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        """Various information regarding bot."""

        g_total = len(self.bot.guilds)
        guilds = (
            f"**Hijinx** is currently in **{g_total}**"
            f" guilds. ([Invite](http://tiny.cc/botgi))"
        )
        embed = discord.Embed(description=guilds)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)
        owner = self.bot.get_user(self.bot.owner_id)
        embed.set_author(name=f"By: {owner}", icon_url=owner.avatar_url)
        embed.set_thumbnail(url="https://hmp.me/cjrp")

        members_total = len(list(self.bot.get_all_members()))
        members_unique = len(self.bot.users)

        m_online = []
        for member in self.bot.get_all_members():
            if member.status != discord.Status.offline:
                m_online.append(member)
        members_online = len(m_online)

        members = (
            f"**{members_total}** total\n"
            f"**{members_unique}** unique\n"
            f"**{members_online}** online"
        )
        embed.add_field(name="Members:", value=members, inline=True)

        c_text = []
        c_voice = []
        for guild in self.bot.guilds:
            c_text.extend(guild.text_channels)
            c_voice.extend(guild.voice_channels)
        text_channels = len(c_text)
        voice_channels = len(c_voice)

        channels = (
            f"**{text_channels + voice_channels}** total\n"
            f"**{text_channels}** text\n"
            f"**{voice_channels}** voice"
        )
        embed.add_field(name="Channels:", value=channels, inline=True)

        latency = round(self.bot.latency * 1000)
        uptime = self.get_uptime(brief=True)
        memory_usage = round(self.process.memory_full_info().uss / 1024 ** 2)
        cpu_usage = round(self.process.cpu_percent() / psutil.cpu_count())
        lines, files = self.get_lines()

        various = (
            f"🏓 {latency}ms │ ✈️ {uptime} │"
            f" 📈 {memory_usage}MiB ~ CPU: {cpu_usage}%"
            f" │ 📝 {lines} lines, {files} files."
        )
        embed.set_footer(text=various)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def info(self, ctx, member=None):
        """Find information about a specified user"""

        if member is None:
            member = ctx.author

        embed = discord.Embed(description=None)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)

        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)


def setup(bot):
    bot.add_cog(Stats(bot))

