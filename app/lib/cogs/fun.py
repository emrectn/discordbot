from discord.ext.commands import Cog, command


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=['hi'])
    async def hello(self, ctx):
        '''Dailybot'a selam söyle :D'''
        await ctx.send(f'Hello! {ctx.author.mention}')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
