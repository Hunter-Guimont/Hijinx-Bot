import discord
from discord.ext import commands
import datetime
import json
import random


def get_prefix(bot_, message):
    prefixes = ['*']
    return commands.when_mentioned_or(*prefixes)(bot_, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    owner_id=222800179697287168
)


# ------ Methods ------
def load_json(path):
    with open(path) as f:
        return json.load(f)
# ---------------------

bot.config = load_json('./cogs/Data/config.json')

initial_extensions = [
    'cogs.Information',
    'cogs.WebSearches',
    'cogs.MusicPlayer',
    'cogs.Entertainment',
    'cogs.ErrorHandler'
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)


# ------ Events ------
@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    activity = discord.Activity(
        name="*",
        type=discord.ActivityType.listening
    )
    await bot.change_presence(
        activity=activity,
    )
    print(
        f'{bot.user.name} - {bot.user.id}\n'
        f'Guilds:  {len(bot.guilds)}\n'
        f'Members: {len(set(bot.get_all_members()))}'
    )


@bot.event
async def on_command(ctx):
    user = ctx.author.name + '#' + ctx.author.discriminator
    guild = ctx.guild.name
    channel = ctx.channel.name
    print(
        f"{user} said: '{ctx.message.content}' on '{guild}' in '{channel}'."
    )


@bot.event
async def on_member_join(user):
    channel = user.guild.system_channel
    if commands.bot_has_permissions(send_message=False):
        return
    with open('./cogs/fun/greetings.json') as f:
        d = json.load(f)

    greeting = random.choice(list(d.values()))
    if channel is not None:
        await channel.send(f"*{greeting.replace('{user}', f'**{user}**')}*")

bot.run(bot.config['token'], bot=True, reconnect=True)
