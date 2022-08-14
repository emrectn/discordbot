import os
import json
from glob import glob
from asyncio import sleep
from pandas import DataFrame

from discord import Intents
from discord.ext.commands import Context
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from discord.ext.commands import BadArgument, CheckFailure, CommandOnCooldown
from discord.ext.commands import Bot as BotBase

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from lib.utils.clock import get_time
from lib.utils.config import settings
from lib.utils.reaction import reaction
from lib.utils.mail_module import EmailTemplate
from lib.utils.trello import get_data_from_trello

""" from data.db.build import list_of_reports
from data.db.build import daily_reports_df """


PREFIX = "!"
OWNER_IDS = list(settings.owner_id)


if os.name == 'nt':
    COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
else:
    COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Ready(object):
    """
    A class to keep track of when all cogs are ready
    """

    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class DailyBot(BotBase):
    """
    Main class of the bot
    """

    def __init__(self):

        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = settings.discord_guild_id
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=PREFIX,
            owner_id=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        """ 
        Load cogs and add them to the bot
        """

        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"Loaded {cog}")
        print("Loaded all cogs")

    def run(self, version):
        """
        Run the bot
        """

        self.VERSION = version
        self.TOKEN = settings.dailybot_token

        print('running setup...')
        self.setup()

        print(f"Starting DailyBot v{self.VERSION}")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None:  # and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("I'm not ready to recieve commands yet please wait a few seconds.")

    async def on_connect(self):
        """
        When the bot connects to Discord
        """

        print("Connected to Discord")

    async def on_disconnect(self):
        """ 
        When the bot disconnects from Discord
        """

        print("Disconnected from Discord")


bot = DailyBot()


# ERROR HANDELING
@bot.event
async def on_error(self, err, *args, **kwargs):
    """
    This event is called when the bot has an error.
    """

    if err == 'on_command_error':
        await args[0].send("An error occured while executing the command.")

    await self.stdout.write(f"An error occured: {err}")
    raise


@bot.event
async def on_command_error(ctx, exc):
    """
    This event is called when a command has an error.
    """

    if isinstance(exc, CommandNotFound):
        await ctx.send(f"Command `{ctx.message.content}` not found")

    elif isinstance(exc, MissingRequiredArgument):
        await ctx.send(f"Missing required argument `{exc.param.name}`")

    elif isinstance(exc, BadArgument):
        await ctx.send(f"Bad argument `{exc.param.name}`")

    elif isinstance(exc, CommandOnCooldown):
        await ctx.send(f"This command is on cooldown for {exc.retry_after:.2f} seconds")

    elif isinstance(exc, CheckFailure):
        await ctx.send(f"You don't have the required permissions to execute this command")

    elif hasattr(exc, 'original'):
        print(f"Unhandled error occured in command `{ctx.command.name}`")
        raise exc.original

    else:
        print(f"Unhandled error occured in command `{ctx.command.name}`")
        raise exc


# SCHEDULED TASKS
def get_user_from_id(user_id):
    for u in members:
        if u.id == user_id:
            return u

""" 
def get_unreported_list(reported):
    un_reported = []
    for u in members:
        if (u.id != bot.user.id) and (u.id not in settings.exclude_list) and (u.id not in reported):
            un_reported.append(u.name)
    return un_reported
 """

""" reported = list_of_reports() """


""" @bot.event
async def member_refresh():
    global members
    members = []

    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                members.append(member) """

""" 
@bot.event
async def reminder():
    reported = list_of_reports()
    for u in members:
        if (u.id == bot.user.id) or (u.id in settings.exclude_list) or (u.id in reported):
            continue

        print(f"sending reminder to {u.name}")
        user_dm_channel_ = u.dm_channel

        try:
            if user_dm_channel_ is None:
                await u.create_dm()
                user_dm_channel_ = u.dm_channel

            await user_dm_channel_.send(
                reaction.standup_text.format(user=u.name))
        except Exception as e:
            print(e)
    print("Done!") """


""" @bot.event
async def daily_mail():
    reported = list_of_reports()
    un_reported = get_unreported_list(reported)
    unreported_df = DataFrame(un_reported, columns=['user_name'])

    EmailTemplate(
        settings.email_username, settings.email_password, 
        [unreported_df, daily_reports_df()]
                  )

    for user_id in settings.supervisor_id:
        user = get_user_from_id(user_id)
        try:
            user_dm_channel_ = user.dm_channel
            if user_dm_channel_ is None:
                await user.create_dm()
                user_dm_channel_ = user.dm_channel
            await user_dm_channel_.send(reaction.un_reported.format(
                get_time()['date'], len(un_reported), "\n- ".join(un_reported))
                )
        except Exception as e:
            print(e) """


""" @bot.event
async def trello_data_sync():
    print("Syncing trello data...")
    member_tasks = get_data_from_trello()

    with open("data/trello_tasks.json", "w") as fp:
        json.dump(member_tasks, fp, indent=4)

    print("Trello sync done") """


# ON READY
@bot.event
async def on_ready():
    """
    This event is called when the bot is ready to start.
    """
    # global members
    if not bot.ready:
        print(f"Logged in as {bot.user.name}")
        bot.guild = bot.get_guild(settings.discord_guild_id)
        bot.standup_channel = bot.get_channel(int(settings.standup_channel_id))
        bot.log_channel = bot.get_channel(906564458812420118)

        # await member_refresh()

        # bot.scheduler.add_job(trello_data_sync, CronTrigger(
        #     day_of_week='0-4', hour='4', minute='30', timezone='Europe/Istanbul'))
        # bot.scheduler.add_job(member_refresh, CronTrigger(
        #     day_of_week='0-4', minute='59', timezone='Europe/Istanbul'))
        # bot.scheduler.add_job(reminder, CronTrigger(
        #     day_of_week='0-4', hour='9, 10, 11', minute='30', timezone='Europe/Istanbul'))
        # bot.scheduler.add_job(daily_mail, CronTrigger(
        #     day_of_week='0-4', hour='18', minute='00', timezone='Europe/Istanbul'))

        # bot.scheduler.start()

        while not bot.cogs_ready.all_ready():
            await sleep(1)

        bot.ready = True
        print('DailyBot ready!')

    else:
        print('DailyBot reconnected')
