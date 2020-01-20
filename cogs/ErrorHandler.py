import sys
import traceback

import discord
from discord.ext import commands

from exceptions import *


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound,
                   commands.UserInputError,
                   commands.errors.CheckFailure)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, discord.errors.Forbidden):
            return await ctx.send(
                "I don't have the permissions required to do that."
            )

        if isinstance(error, BadRequestError):
            return print(
                'Apparent client error caused the request to fail.'
            )

        if isinstance(error, ForbiddenError):
            return await ctx.send(
                'Command is unavailable at the moment, try again later.'
            )

        if isinstance(error, NotFoundError):
            return await ctx.send(
                'Could not find any results for your search.'
            )

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
