# -*- coding: utf-8 -*-

from discord.ext import commands
import discord

import asyncpg

class Reminders(commands.Cog):
    """The description for Reminders goes here."""

    def __init__(self, bot):
        self.bot = bot

    

def setup(bot):
    bot.add_cog(Reminders(bot))
