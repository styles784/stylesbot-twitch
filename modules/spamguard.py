import logging
import re
import twitchio
from twitchio.ext import commands

from config import configuration

logging.config.dictConfig(configuration["LOGGING"])


class SpamGuard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.event()
    async def event_message(self, msg: twitchio.Message) -> None:
        """Checks all incoming messages for regex match
        Matched messages are purged, all others are
        passed on to the main message handler
        """
        if msg.echo:
            return
        p: re.Pattern[str] = re.compile(
            "view(?>er)?[sz]|follow(?>er)?[sz]|prime[sz]|sub(?>scriber)?[sz]",
            re.IGNORECASE
        )
        m: list = p.findall(msg.content)
        if len(m) >= 3:
            logging.debug(f"MATCH: {m}")
            logging.warn(
                f"[CHANNEL: {msg.channel.name}] Deleting possible spam from <{msg.author.display_name}>: {msg.content}"
            )
            # await msg.channel.send(f"/delete {msg.id}")
            broadcaster = await msg.channel.user()
            usr = self.bot.create_user(broadcaster.id, broadcaster.name)
            await usr.delete_chat_messages(
                configuration["SECRET"]["oauth"].split(":")[1], self.bot.user_id, msg.id
            )


def prepare(bot: commands.Bot):
    logging.debug("Preparing SpamGuard...")
    bot.add_cog(SpamGuard(bot))
