import json
import random as ran
from string import capwords

from discord.ext import commands


class FunCommands(commands.Cog):
    """Random commands provided for your amusement."""

    def __init__(self, bot):
        self.bot = bot
        self.rps_choices = self.load_rps_choices()
        self.eightball = self.load_eightball_choices()

    @staticmethod
    def load_rps_choices():
        with open('./cogs/fun/rps101.json') as f:
            return json.load(f)

    @commands.command()
    async def rps101(self, ctx, choice):
        """101-gesture version of Rock-Paper-Scissors."""

        choices = self.rps_choices
        if choice not in choices:
            return
        opponent = ran.choice(list(choices))

        if choice == opponent:
            r = f". {ran.choice(['stalemate', 'tie', 'draw'])}, Everyone Loses!"
        elif opponent in choices[choice]:
            r = f". {choice} {choices[choice][opponent]} {opponent}, You Win!"
        elif choice in choices[opponent]:
            r = f". {opponent} {choices[opponent][choice]} {choice}, You Lose!"
        else:
            return print(f"Choice = {choice}, Opponent = {opponent}")

        return await ctx.send(ctx.author.mention + capwords(r))

    @staticmethod
    def load_eightball_choices():
        with open('./cogs/fun/eightball.json') as f:
            return json.load(f)

    @commands.command(name='8ball')
    async def eightball(self, ctx, *, question):
        """Magic 8 Ball for fortune-telling or seeking advice."""

        choices = self.eightball
        if not question[-1] == '?':
            question += '?'
        answer = choices[f'{ran.choice(list(choices))}']
        await ctx.send(f'*"{question.capitalize()}"* - '
                       f'{ctx.author.mention}. *{answer}*')

    @commands.command()
    async def choose(self, ctx, *, args):
        """Chooses a random option out of a coma separated list."""

        choices = ' '.join(args).split(',')
        choice = ran.choice(choices)
        await ctx.send(f'{ctx.author.mention}. I choose *"{choice.strip()}"*.')

    @commands.command()
    async def taunt(self, ctx, *, text):
        """Sticky caps (alternating case) string converter."""

        new = ""
        case = ran.choice([True, False])
        for char in text:
            if case:
                new += char.upper()
            else:
                new += char.lower()
            if char != ' ':
                case = not case
        await ctx.send(f"*{new}*")

    @commands.command()
    async def say(self, ctx, *, text):
        """Repeats whatever you include in the command."""

        await ctx.send(text)


def setup(bot):
    bot.add_cog(FunCommands(bot))
