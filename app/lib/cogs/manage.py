from discord.ext.commands import Cog, command


class Manage(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("manage")

    @Cog.listener()
    async def on_message(self, message):
        '''komut aktif test'''
        if message.content.startswith("!test"):
            await message.channel.send("test")


def setup(bot):
    bot.add_cog(Manage(bot))
