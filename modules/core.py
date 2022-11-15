import logging
import logging.config

# import twitchio
from twitchio.ext import commands

from config import configuration

logging.config.dictConfig(configuration["LOGGING"])


class CoreModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context):
        if ctx.author.is_mod:
            await ctx.reply(f"It's okay to ask for help, {ctx.author.display_name}")


def prepare(bot: commands.Bot):
    bot.add_cog(CoreModule(bot))
