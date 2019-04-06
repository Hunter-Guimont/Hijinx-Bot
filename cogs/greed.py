from discord.ext import commands


class GreedIsland(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(case_insensitive=True)
    async def stats(self, ctx):
        """Displays your current stats and progress. (only money rn)"""
        await ctx.send(f'You have a total of {ctx.self.bot.player.wallet} jenny.')


def setup(bot):
    bot.add_cog(GreedIsland(bot))
