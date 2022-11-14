import logging
import logging.config
from twitchio.ext import commands
import config
from config import configuration

logging.config.dictConfig(configuration["LOGGING"])


class StylesBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=configuration["SECRET"]["oauth"],
            prefix=configuration["OPTIONS"]["prefix"],
            client_secret=configuration["SECRET"]["client_secret"],
            initial_channels=configuration["OPTIONS"]["channels"],
        )

    async def event_ready(self):
        if self.nick not in [c.name for c in self.connected_channels]:
            await self.join_channels([self.nick])
        logging.info(f"Logged in as | {self.nick}")

    @commands.command(name="load")
    async def load_cog(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        modname = ctx.message.content.split(" ")[1]
        logging.info(f"Attempting to load {modname}")
        self.load_module(modname)

    @commands.command(name="unload")
    async def unload_cog(self, ctx: commands.Context):
        if ctx.author.is_mod:
            modname = ctx.message.content.split(" ")[1]
            print(f"Attempting to unload {modname}")
            self.unload_module(modname)

    @commands.command(name="reload")
    async def reload_cog(self, ctx: commands.Context):
        if ctx.author.is_mod:
            modname = ctx.message.content.split(" ")[1]
            print(f"Attempting to reload {modname}")
            self.reload_module(modname)

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.is_mod:
            channels = ctx.message.content.split(" ")[1:]
            await self.join_channels(channels)
            await ctx.reply(f"Joined {channels}")
            logging.info(f"Now watching users in {channels}")

    @commands.command()
    async def leave(self, ctx: commands.Context):
        if ctx.author.is_mod:
            channels = ctx.message.content.split(" ")[1:]
            await self.part_channels(channels)
            logging.info(f"Leaving {channels}")

    @commands.command()
    async def channels(self, ctx: commands.Context):
        if ctx.author.is_mod:
            await ctx.reply(
                f"Currently watching: {[c.name for c in self.connected_channels if c is not None]}"
            )

    @commands.command()
    async def lsmod(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == self.nick:
            logging.debug(f"Modules: {[m for m in self.cogs.keys()]}")
            await ctx.send(f"Modules: {self.cogs.keys()}")

    @commands.command()
    async def save(self, ctx: commands.Context) -> None:
        if not ctx.author.name == self.nick:
            return
        with open("config.json", "w") as f:
            channels = [c.name for c in self.connected_channels]
            modules = list(self.cogs.keys())
            config.save(channels, modules)
            logging.info("Settings saved to config.json")

    @commands.command()
    async def quit(self, ctx: commands.Context):
        if ctx.author.name == ctx.channel.name:
            await self.part_channels(ctx.author.name)
        elif ctx.author.name == self.nick:
            logging.critical(f"ABORTING per {ctx.author.name}'s request!")
            await self.close()
            quit()


if __name__ == "__main__":

    bot = StylesBot()
    for m in configuration["OPTIONS"]["modules"]:
        bot.load_module(f"modules.{m}")
    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    channels: list[str] = [c.name for c in bot.connected_channels]
    modules: list[str] = [m.lower().removesuffix("module") for m in bot.cogs.keys()]
    config.save(channels, modules,)

    print("Bye!")
