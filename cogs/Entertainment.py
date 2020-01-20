import json
import random as ran
import string
from typing import Union
from string import capwords
from collections import deque
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


class FunCommands(commands.Cog, name='Fun'):
    """Random commands provided for your entertainment."""

    def __init__(self, bot):
        self.bot = bot

    # ------ Methods ------
    @staticmethod
    def load_json(path):
        with open(path) as f:
            return json.load(f)

    # ------ Commands ------
    @commands.command(name='rps', aliases=['jajanken'])
    async def rock_paper_scissors(self, ctx, choice):
        """Rock, Paper, Scissors but with 5,050 possible outcomes."""
        choices = self.load_json('./cogs/Data/RockPaperScissors.json')
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
            r = 'Data seems to be incomplete, try again for a different result.'
        return await ctx.send(ctx.author.mention + capwords(r))

    @commands.command(name='8ball', aliases=['eightball'])
    async def eight_ball(self, ctx, *, question: commands.clean_content):
        """Magic 8 Ball for fortune-telling or seeking advice."""
        choices = self.load_json('./cogs/Data/Magic8Ball.json')
        if not question[-1] == '?':
            question += '?'
        answer = choices[f'{ran.choice(list(choices))}']
        await ctx.send(
            f'*"{question.capitalize()}"* - '
            f'{ctx.author.mention}. *{answer}*'
        )

    @commands.command(name='choose')
    async def random_choice(self, ctx, *, args: commands.clean_content):
        """Chooses a random option out of a coma separated list."""
        choices = args.split(',')
        choice = ran.choice(choices)
        await ctx.send(f'{ctx.author.mention}. I choose *"{choice.strip()}"*.')

    @commands.command(aliases=['repeat', 'simon says'])
    async def say(self, ctx, *, text: commands.clean_content):
        """Repeats whatever you include in the command."""
        await ctx.send(text)

    @commands.command(name='taunt', aliases=['mock'])
    async def sticky_caps(self, ctx, *text: Union[str, commands.clean_content]):
        """Sticky caps (alternating case) string converter."""
        new = ''
        x=0
        for char in ' '.join(text):
            new += (2*char).title()[x]
            x ^= char.isalpha()
        await ctx.send(f"**{new}**")

    @commands.command()
    async def encode(self, ctx, offset: int, *text: Union[str, commands.clean_content]):
        """Make secret messages that """
        all_chars = list(string.ascii_letters)
        rotated_chars = deque(all_chars)
        rotated_chars.rotate(offset)
        d = dict(zip(all_chars, rotated_chars))
        encrypted = [d[char] if char in d else char for char in text]
        if not encrypted:
            return
        await ctx.send(''.join(encrypted).replace('\t', '\\'))

    @commands.command()
    async def decode(self, ctx, offset: int, *text: Union[str, commands.clean_content]):
        await ctx.invoke(self.encode, -offset, text=text)

    @commands.command(name='coinflip', aliases=['flip'])
    async def coin_flip(self, ctx):
        await ctx.send(f"You got {ran.choice(['Heads!', 'Tails!'])}")

    @commands.command(name='diceroll', aliases=['roll'])
    async def dice_roll(self, ctx, amount: int = 1):
        join = ", "
        results = []
        if amount > 3 or amount <= 0:
            return await ctx.send('Can only roll 1-3 dice at once. :game_die:')

        if amount > 1:
            for _ in range(amount):
                results.append(str(ran.choice(range(1, 7))))
            results[-1] = 'and ' + results[-1]
            if amount == 2:
                join = ' '
            results = join.join(results)
        else:
            results = ran.choice(range(1, 7))
        await ctx.send(f"You rolled a {results}. " + ':game_die: '*amount)

    @commands.command(name='fan')
    async def fan_text(self, ctx, *, text: Union[discord.Emoji, str]):
        text = [char for char in text]
        output = ''
        for i in range(10):
            output += (i*' ').join(text) + '\n'
        if len(output) > 2000:
            return await ctx.send(
                'Message was too long to return. Try something shorter.'
            )
        await ctx.send(output)

    @commands.command()
    async def topic(self, ctx):
        """
        Gets a random chat topic to keep the chat going.
        """
        website = requests.get('https://www.conversationstarters.com/generator.php').content
        soup = BeautifulSoup(website, 'html.parser')
        topic = soup.find(id="random").text
        await ctx.send(topic)


def setup(bot):
    bot.add_cog(FunCommands(bot))
