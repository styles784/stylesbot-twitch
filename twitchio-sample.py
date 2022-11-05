# from asyncio import sleep
import requests
import json

# import re
# import urllib.parse
# import webbrowser
# import binascii
# import os
# import time
import logging
import logging.config

# from http.server import HTTPServer, BaseHTTPRequestHandler
# from modules.spamguard import SpamCog
import twitchio
from twitchio.ext import commands, routines  # eventsub
import modules.twitchinsights as twitchinsights

# import authorize
import config

logging.config.dictConfig(config.LOGGING)


class StylesBot(commands.Bot):
    # blacklist: str
    def __init__(self):
        super().__init__(
            token=config.oauth,
            prefix=config.prefix,
            client_secret=config.client_secret,
            initial_channels=config.channels,
        )

        logging.debug("Preparing to grab bot list from TwitchInsights.net...")
        logging.debug("Grabbing bot list...")
        self.botlist = twitchinsights.BotList()
        self.seen = []
        # self.follows = {}
        logging.info(f"Bot list retrieved - watching for {self.botlist.count()} bots")

        # routines
        # self.refresh_bots.start()

    # @routines.routine(hours=6)
    # async def refresh_bots(self):
    #     self.botlist.update()
    #     logging.info(f"Refreshed list | {self.botlist.count()} known bots")

    # def get_auth(self, client_id, client_secret):
    #     grant_type = "client_credentials"
    #     url = "https://id.twitch.tv/oauth2/token"
    #     params = {
    #         "client_id": client_id,
    #         "client_secret": client_secret,
    #         "grant_type": "client_credentials",
    #     }
    #     logging.debug(url)
    #     response = requests.post(url, params)
    #     token = json.loads(response.text)

    #     return token

    # async def get_followers(self, channel):
    #     # channel.user.id
    #     broadcaster = await channel.user()
    #     url = "https://api.twitch.tv/helix/users/follows"
    #     params = {"to_id": broadcaster.id}
    #     token = " ".join([self.auth["token_type"].title(), self.auth["access_token"]])
    #     header = {"Client-ID": client_id, "authorization": token}

    #     response = requests.get(url, params=params, headers=header)
    #     followers = json.loads(response.text)

    #     return followers

    # async def check_user(self, user: str, channel: twitchio.Channel):
    #     if user not in self.seen:
    #         logging.debug(f"{user} | seen: {user in self.seen}")
    #         if user in self.botlist.ToList():
    #             logging.debug(f"POSSIBLE BOT DETECTED in {channel.name}: {user}")
    #             logging.info(
    #                 f"Banning suspected bot | user: {user} | channel: {channel.name}"
    #             )
    #             await channel.send(
    #                 f"/ban {user} suspected bot - please send an unban request if a mistake has been made"
    #             )
    #         else:
    #             logging.debug(f"Saw {user} for the first time")
    #             self.seen.append(user)

    # async def check_all(self):
    #     url = "https://tmi.twitch.tv/group/user/{name}/chatters"
    #     for channel in self.connected_channels:
    #         if channel is not None:
    #             logging.debug(f"Checking channel {channel.name}")
    #             response = requests.get(url.format(name=channel.name))
    #             chatters = json.loads(response.text)["chatters"]["viewers"]
    #             for user in chatters:
    #                 await self.check_user(user, channel)

    async def event_ready(self):
        logging.info(f"Logged in as | {self.nick}")
        # await self.check_all()

    # async def event_join(self, channel, user):
    #     logging.debug(f"{user.name} has joined {channel}")

    #     await self.check_user(user.name, channel)

    @commands.command(name="load")
    async def load_cog(self, ctx: commands.Context):
        if ctx.author.is_mod:
            modname = ctx.message.content.split(" ")[1]
            print(f"Attempting to load {modname}")
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

    # @commands.command(name="mban")
    # async def mass_ban(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         names = ctx.message.content.split(" ")[1:]
    #         for channel in self.connected_channels:
    #             for name in names:
    #                 logging.info(f"Banning {name} in {channel.name}")
    #                 await channel.send(f"/ban {name} another bot")

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.author.is_mod:
            channels = ctx.message.content.split(" ")[1:]
            await self.join_channels(channels)
            await ctx.reply(f"Joined {channels}")
            await self.check_all()
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

    # @commands.command(aliases=["unban"])
    # async def allow(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         users = ctx.message.content.split(" ")[1:]
    #         for user in users:
    #             self.botlist.allow(user)
    #             logging.info(f"Whitelisted {user} as requested by {ctx.author.name}")
    #             for channel in self.connected_channels:
    #                 await channel.send(f"/unban {user}")

    # @commands.command()
    # async def disallow(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         users = ctx.message.content.split(" ")[1:]
    #         for user in users:
    #             self.botlist.disallow(user)
    #             logging.info(f"Blacklisted {user} as requested by {ctx.author.name}")

    # @commands.command()
    # async def remove(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         names = ctx.message.content.split(" ")[1:]
    #         for user in names:
    #             self.botlist.remove(user)
    #             logging.info(f"Removed {user} from all lists")

    # @commands.command()
    # async def numbots(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         size = self.botlist.count()
    #         await ctx.reply(f"There are {size} known bots curently online")

    # @commands.command()
    # async def verify(self, ctx: commands.Context):
    #     if ctx.author.is_mod:
    #         name = ctx.message.content.split(" ")[1]
    #         await ctx.send("I'll check my list...")
    #         if name.lower() in self.botlist.ToList():
    #             await ctx.reply(f"{name} is in the list")
    #         else:
    #             await ctx.reply(f"{name} not found")

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
    bot.load_module("modules.core")
    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print("Bye!")
