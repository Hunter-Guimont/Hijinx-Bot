import datetime
from os import walk
from os.path import join

import discord
import humanfriendly
import psutil
from discord.ext import commands
from typing import Union


class InformationCommands(commands.Cog, name='Information'):
    """Hopefully the answers you're looking for..."""
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    # ------ Methods ------
    # ------ Stats
    @staticmethod
    def get_line_count():
        py_files = []
        for root, _, files in walk('.'):
            py_files += (
                [join(root, file) for file in files if file.endswith('.py')]
            )
        line_count = 0
        for file in py_files:
            with open(file) as f:
                line_count += len(
                    [line for line in f if not line == '']
                )
        return line_count, len(py_files)

    def get_up_time(self, *, brief=False):
        now = datetime.datetime.now()
        start_time = self.bot.start_time
        delta = round((now - start_time).total_seconds())
        time = humanfriendly.format_timespan(delta)
        if brief:
            time = (time.replace(',', '').replace('and', '')).split()
            words = [item[0] + ' ' if item.isalpha() else item for item in time]
            time = ''.join(words)
        return time

    def get_latency(self):
        return round(self.bot.latency * 1000)

    def get_resource_usage(self):
        memory_usage = round(self.process.memory_full_info().uss / 1024 ** 2)
        cpu_usage = round(self.process.cpu_percent() / psutil.cpu_count())
        return memory_usage, cpu_usage

    # ------ Display
    @staticmethod
    async def minimal_embed(ctx, name=None, text=None, image=None):
        embed = discord.Embed(
            description=text,
            color=discord.Color.from_rgb(0, 100, 225)
        )
        embed.set_author(name=name or '')
        embed.set_image(url=image or '')
        await ctx.send(embed=embed)

    # ------ Commands ------
    @commands.command(aliases=['runtime'])
    async def uptime(self, ctx):
        """Displays time since bot went online."""
        await self.minimal_embed(ctx, text=f"**✈️ {self.get_up_time()}.**")

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        """Displays bots latency."""
        await self.minimal_embed(ctx, text=f"**🏓 {self.get_latency()}ms**")

    @commands.command(aliases=['about'])
    async def botinfo(self, ctx):
        """Various information regarding bot."""
        # ------ Input
        bot_owner = self.bot.get_user(self.bot.owner_id)
        guilds_total = len(self.bot.guilds)

        m_online = []
        for member in self.bot.get_all_members():
            if member.status != discord.Status.offline:
                m_online.append(member)
        members_online = len(m_online)
        members_unique = len(self.bot.users)
        members_total = len(list(self.bot.get_all_members()))

        c_text = []
        c_voice = []
        for guild in self.bot.guilds:
            c_text.extend(guild.text_channels)
            c_voice.extend(guild.voice_channels)
        channels_text = len(c_text)
        channels_voice = len(c_voice)
        channels_total = channels_text + channels_voice

        latency = self.get_latency()
        up_time = self.get_up_time(brief=True)
        line_count, file_count = self.get_line_count()
        memory_use, cpu_use = self.get_resource_usage()

        # ------ Processing / Output
        description = (
            f"**Hijinx** is currently in **{guilds_total}**"
            f" guilds. ([Invite](http://tiny.cc/botgi))"
        )
        members = (
            f"**{members_total}** total\n"
            f"**{members_unique}** unique\n"
            f"**{members_online}** online"
        )
        channels = (
            f"**{channels_total}** total\n"
            f"**{channels_text}** text\n"
            f"**{channels_voice}** voice"
        )
        footer = (
            f"🏓 {latency}ms │ ✈️ {up_time} │"
            f" 📈 {memory_use}MiB ~ CPU: {cpu_use}%"
            f" │ 📝 {line_count} lines, {file_count} files."
        )
        embed = discord.Embed(description=description)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)
        embed.set_author(name=f"By: {bot_owner}", icon_url=bot_owner.avatar_url)
        embed.set_thumbnail(url="https://hmp.me/cjrp")
        embed.add_field(name="Members:", value=members, inline=True)
        embed.add_field(name="Channels:", value=channels, inline=True)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    @commands.group(aliases=['user'], invoke_without_command=True)
    async def userinfo(self, ctx, person: Union[discord.Member, discord.User] = None):
        """Find information about a specified Discord user."""
        # ------ Variables
        person = person or ctx.author
        color = discord.Color(0x747f8d)
        join_date = 'Never'
        role_list = 'User is not currently a member of this guild.'
        device = ':detective: Device type is unavailable.'
        activity = ':sleeping: No activity right now.'

        # ------ Input / Processing
        create_date = person.created_at.strftime('%m/%d/%Y')
        if isinstance(person, discord.Member):
            join_date = person.joined_at.strftime('%m/%d/%Y')
            if person.status == discord.Status.online:
                color = discord.Color(0x43b581)
            elif person.status == discord.Status.dnd:
                color = discord.Color(0xf04747)
            elif person.status == discord.Status.idle:
                color = discord.Color(0xfaa61a)
            if person.status != discord.Status.offline:
                if person.is_on_mobile():
                    device = ':iphone: On a mobile device.'
                else:
                    device = ':computer: On a desktop device.'

            role_list = []
            for role in person.roles[1:][:25]:
                role_list.append(role.mention)
            role_list.reverse()
            role_list = ' '.join(role_list)

            if person.activity is not None:
                activity_type = person.activity.type
                if activity_type == discord.ActivityType.playing:
                    activity = f':video_game: Playing "{person.activity.name}".'
                elif activity_type == discord.ActivityType.watching:
                    activity = f':tv: Watching "{person.activity.name}".'
                elif activity_type == discord.ActivityType.listening:
                    activity = f':notes: Listening to "{person.activity.name}".'
                else:
                    activity = f':interrobang: Engaged in custom activity.'

        if person.bot:
            device = ':robot: This user is a bot.'

        name = person.name + '#' + person.discriminator
        if person.display_name != person.name:
            name = person.display_name + f'  |  ({name})'

        # ------ Output
        display = (
            f'{activity}\n'
            f'{device}\n'
            f':snowflake: {person.id}.'
        )
        footer = (
            f'Created on: {create_date} ~ Joined on: {join_date}'
        )
        embed = discord.Embed(description=role_list, color=color)
        embed.set_author(name=name, icon_url=person.avatar_url)
        embed.add_field(name="Here's what I found:", value=display)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    @userinfo.command(aliases=['a', 'i'])
    async def avatar(self, ctx, person: Union[discord.Member, discord.User] = None):
        person = person or ctx.author
        await self.minimal_embed(
            ctx,
            name=person.display_name,
            image=person.avatar_url_as(static_format="png")
        )

    @commands.group(aliases=['guild'], invoke_without_command=True)
    async def guildinfo(self, ctx, guild: int = None):
        """Find information about a specified Discord guild."""
        # ------ Input
        guild = self.bot.get_guild(guild) or ctx.guild

        # ------ Processing
        create_date = guild.created_at.strftime('%m/%d/%Y')
        m_online = []
        m_bots = []
        for member in guild.members:
            if member.status != discord.Status.offline:
                m_online.append(member)
            if member.bot:
                m_bots.append(member)
        members_online = len(m_online)
        members_bots = len(m_bots)

        c_nsfw = []
        for channel in guild.text_channels:
            if channel.is_nsfw():
                c_nsfw.append(channel)
        channels_nsfw = len(c_nsfw)

        channels_text = len(guild.text_channels)
        channels_voice = len(guild.voice_channels)
        channels_total = channels_text + channels_voice

        emojis = ' '.join([str(emoji) for emoji in guild.emojis])
        # ------ Output
        author = (
            f'{guild.name} [{guild.region}] (Owned by: {guild.owner})'
        )
        display = (
            f':bust_in_silhouette: **{guild.member_count}** Members: '
            f'**{members_online}** Online / '
            f'**{members_bots}** Bots\n'

            f':busts_in_silhouette: **{channels_total}** Channels: '
            f'**{channels_text - channels_nsfw}** SFW Text / '
            f'**{channels_nsfw}** NSFW Text / '
            f'**{channels_voice}** Voice\n'

            f':snowflake: *{guild.id}*.'
        )
        footer = (
            f'Created on: {create_date}'
        )
        embed = discord.Embed(description=emojis)
        embed.colour = discord.Colour.from_rgb(0, 100, 225)
        embed.set_author(name=author, icon_url=guild.icon_url)
        embed.add_field(name="Here's what I found:", value=display)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    @guildinfo.command(aliases=['a', 'i'])
    async def icon(self, ctx, guild: int = None):
        guild = self.bot.get_guild(guild) or ctx.guild
        await self.minimal_embed(
            ctx,
            name=guild.name,
            image=guild.icon_url
        )


def setup(bot):
    bot.add_cog(InformationCommands(bot))
