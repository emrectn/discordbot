import os
from dotenv import load_dotenv

load_dotenv('dailybot/.env')


class Settings:
    """
    Class to store the settings for the application.
    """

    def __init__(self):
        # Discord
        self.dailybot_token = os.getenv("DAILYBOT_TOKEN")
        self.dailybot_prefix = os.getenv("DAILYBOT_PREFIX")
        self.command_list = ['daily', 'dailyall', 'update', 'help', 'weekly']
        self.discord_guild = os.getenv("DISCORD_GUILD")
        self.discord_guild_id = os.getenv("DISCORD_GUILD_ID")
        self.standup_channel_id = os.getenv("STANDUP_CHANNEL_ID")

        self.owner_id = os.getenv("OWNER_ID")
        self.reminder_time = os.getenv("REMINDER_TIME")
        self.exclude_list = [
        ]
        self.supervisor_id = [
            876735003642462218,  # Emre
        ]

        # Mail
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.daily_mail_time = os.getenv("DAILY_MAIL_TIME")
        self.email_from = 'dailybot@tai-lab.com'
        self.email_subject = 'Dailybot Standups'
        self.email_to = ['emre.cetin@turkcell.com.tr']
        self.email_cc = []

        # Database
        self.mongo_uri = os.getenv("MONGO_URI")

        # Trello
        self.trello_key = os.getenv("TRELLO_KEY")
        self.trello_token = os.getenv("TRELLO_TOKEN")


settings = Settings()
