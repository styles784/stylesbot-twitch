import json
import logging
import requests
import twitchio
from twitchio.ext import commands, routines
from .twitchinsights import BotList
from config import configuration

logging.config.dictConfig(configuration["LOGGING"])


class BotFilter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.botlist: BotList = BotList()
        self.seen: list[str] = []
        self.refresh_bots.start()

    @commands.Cog.event()
    async def event_join(self, channel, user):
        if channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        logging.debug(f"{user.name} spotted in {channel.name}")
        await self.check_user(user.name, channel)

    @commands.Cog.event("event_channel_joined")
    async def sweepclear(self, channel: twitchio.Channel):
        url = "https://tmi.twitch.tv/group/user/{name}/chatters"
        response = requests.get(url.format(name=channel.name))
        chatters = json.loads(response.text)["chatters"]["viewers"]
        for user in chatters:
            await self.check_user(user, channel)

    @routines.routine(hours=6)
    async def refresh_bots(self):
        logging.debug("Preparing to grab bot list from TwitchInsights.net...")
        logging.debug("Grabbing bot list...")
        self.botlist.update()
        logging.info(f"Refreshed list | {self.botlist.count()} known bots")
        await self.check_all()

    @commands.command()
    async def enable(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        args: list[str] = ctx.message.content.split(" ")
        channel = args[1] if len(args) > 1 else ctx.channel.name
        if channel in configuration["OPTIONS"]["enabled"]:
            return
        configuration["OPTIONS"]["enabled"].append(channel)
        logging.info(f"Enabled botfilter in {channel}")

    @commands.command()
    async def disable(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        args: list[str] = ctx.message.content.split(" ")
        channel = args[1] if len(args) > 1 else ctx.channel.name
        if channel not in configuration["OPTIONS"]["enabled"]:
            return
        configuration["OPTIONS"]["enabled"].remove(channel)
        logging.info(f"Disabled botfilter in {channel}")

    @commands.command(name="enabled")
    async def is_enabled(self, ctx: commands.Context) -> None:
        if not ctx.author.is_mod:
            return
        await ctx.send(f'Enabled in {configuration["OPTIONS"]["enabled"]}')

    @commands.command()
    async def status(self, ctx: commands.Context) -> None:
        if not ctx.author.is_mod:
            return
        await ctx.send(f'Filter enabled: {ctx.channel.name in configuration["OPTIONS"]["enabled"]}')

    @commands.command()
    async def permtest(self, ctx: commands.Context) -> None:
        if ctx.channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        await ctx.send(f'Permission has been granted in {ctx.channel.name}')

    @commands.command(aliases=["unban"])
    async def allow(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        if ctx.channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        users = ctx.message.content.split(" ")[1:]
        for user in users:
            self.botlist.allow(user)
            logging.info(f"Whitelisted {user} as requested by {ctx.author.name}")
            for channel in self.bot.connected_channels:
                await channel.send(f"/unban {user}")

    @commands.command(aliases=["ban"])
    async def disallow(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        if ctx.channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        users = ctx.message.content.split(" ")[1:]
        for user in users:
            self.botlist.disallow(user)
            logging.info(f"Blacklisted {user} as requested by {ctx.author.name}")

    @commands.command(name="mban")
    async def mass_ban(self, ctx: commands.Context):
        if not ctx.author.is_mod:
            return
        if ctx.channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        names = ctx.message.content.split(" ")[1:]
        for channel in self.bot.connected_channels:
            for name in names:
                logging.info(f"Banning {name} in {channel.name}")
                await channel.send(f"/ban {name} another bot")

    @commands.command()
    async def numbots(self, ctx: commands.Context):
        if ctx.author.is_mod or ctx.author.name == self.bot.nick:
            size = self.botlist.count()
            await ctx.reply(f"I know of {size} known bots")

    @commands.command()
    async def verify(self, ctx: commands.Context):
        if not (ctx.author.is_mod or ctx.author.name == self.bot.nick):
            return
        name = ctx.message.content.split(" ")[1]
        if name.lower() in self.botlist.ToList():
            await ctx.reply(f"{name} might be a bot")
        else:
            await ctx.reply(f"{name} is not on my list")

    async def check_user(self, user: str, channel: twitchio.Channel):
        if channel.name not in configuration["OPTIONS"]["enabled"]:
            return
        hval = f"{user}{channel.name}"
        if hval not in self.seen:
            logging.debug(f"{user} spotted in {channel.name}")
            if user in self.botlist.ToList():
                logging.debug(f"POSSIBLE BOT DETECTED in {channel.name}: {user}")
                logging.info(
                    f"Banning suspected bot | user: {user} | channel: {channel.name}"
                )
                await channel.send(
                    f"/ban {user} suspected bot - please send an unban \
                        request if a mistake has been made"
                )
            else:
                logging.debug(f"Saw {user} for the first time")
                self.seen.append(hval)

    async def check_all(self):
        url = "https://tmi.twitch.tv/group/user/{name}/chatters"
        for channel in self.bot.connected_channels:
            if channel is not None:
                logging.debug(f"Checking channel {channel.name}")
                response = requests.get(url.format(name=channel.name))
                chatters = json.loads(response.text)["chatters"]["viewers"]
                for user in chatters:
                    await self.check_user(user, channel)


def prepare(bot: commands.Bot):
    logging.debug("Preparing BotFilter")
    bot.add_cog(BotFilter(bot))
