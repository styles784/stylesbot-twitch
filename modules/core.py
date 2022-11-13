import logging
import logging.config
import json

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

    @commands.command()
    async def lsmod(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == self.bot.nick:
            logging.debug(f"Modules: {[m for m in self.bot.cogs.keys()]}")
            await ctx.send(f"Modules: {self.bot.cogs.keys()}")

    @commands.command()
    async def save(self, ctx: commands.Context) -> None:
        if not ctx.author.name == self.bot.nick:
            return
        with open("config.json", "w") as f:
            channels = self.bot.connected_channels
            configuration["OPTIONS"]["channels"] = [c.name for c in channels]
            json.dump(configuration["OPTIONS"], f, indent="\t")
            logging.info("Settings saved to config.json")


def prepare(bot: commands.Bot):
    bot.add_cog(CoreModule(bot))
