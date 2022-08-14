from discord import Member
from discord.ext.commands import Cog, command
from discord import File
from io import StringIO
from asyncio import TimeoutError
from datetime import datetime

# from lib.db import mongo
from lib.utils.clock import get_time, now_time
from lib.utils.config import settings
from lib.utils.reaction import reaction
from lib.utils.utils import fix_null_partition
from lib.utils.embeds import create_embed
# from data.db.build import build_structure, get_weekly_data
# from data.db.build import list_of_reports


def msg_is_suitable(message):
    if message.startswith("!"):
        return False
    return True


sample_standup = reaction.sample_standup


class Daily(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        pass

    @command(name='daily', aliases=['d'])
    async def daily(self, ctx):
        '''
        Bu komutu kullanarak daily raporunu yazabilirsiniz.
        '''
        print(ctx.author.display_name, 'daily command start', now_time())
        
        await ctx.invoke(self.bot.get_command('tasks'))
        
        standup = {'done': '',
                   'wip': '',
                   'blockers': ''}

        if ctx.author == self.bot.user:
            return

        if not (ctx.channel.id == ctx.author.dm_channel.id):
            await ctx.author.send("Bu komutu sadece dm kanalında kullanabilirsiniz.")
            return

        def check(author):
            def inner_check(ctx):
                return ctx.author == author
            return inner_check

        try:

            # done part
            await ctx.send('Dün neler tamamladınız? (Done)')
            msg = await self.bot.wait_for('message', check=check(ctx.author), timeout=100)

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return

            standup['done'] = msg.content

            # wip part
            await ctx.channel.send("Bugün neler yapıcaksın? (Wip)")
            msg = await self.bot.wait_for('message', timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return

            standup['wip'] = msg.content

            # blockers part
            await ctx.channel.send("Bunları yapmana mani olan birşey var mı? (Blockers)")
            msg = await self.bot.wait_for('message', timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return

            standup["blockers"] = msg.content

            await ctx.channel.send(reaction.confirm_text.format(
                standup.get('done').strip(), standup.get('wip').strip(), standup.get('blockers').strip()))
            msg = await self.bot.wait_for('message', timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- !daily veya !update komutu çalıştı. Bir üstteki sorudan devam edebilirsiniz.")
                return

            if msg.content.lower() != 'y':
                await ctx.reply("Raporu göndermediniz. Lütfen tekrar deneyin.")
                return

        except TimeoutError:
            await ctx.reply("Raporu göndermediniz. Lütfen tekrar deneyin.")
            return

        except Exception as e:
            print(e)
            await ctx.reply('Bir hata oluştu. Lütfen tekrar deneyin.')

        else:
            data = mongo.daily_db.reports.find_and_modify(
                {'info.user_id': ctx.author.id,
                    'info.date': get_time()['date']},
                {'$set': build_structure(ctx.author, standup)}, new=True)

            if data:
                await self.bot.standup_channel.send(embed=create_embed(ctx, data['report'], reaction.update_title))
                await ctx.channel.send("İyi Çalışmalar. Daily Raporunu güncelliyorum :)")
            else:
                mongo.daily_db.reports.insert(
                    build_structure(ctx.author, standup))
                await self.bot.standup_channel.send(embed=create_embed(ctx, standup, reaction.info_title))
                await ctx.channel.send("İyi Çalışmalar. Daily Raporunu yolladım :)")
        
        print(ctx.author.display_name, 'daily command end', now_time())

    @command(name='update', aliases=['u'])
    async def _update(self, ctx, arg=None):
        """
        Daily Raporumu verdim ama bir bölümünü güncellemek istiyorsan doğru yerdesin.
        !update done/wip/blockers seçeneklerinden birini kullanmalısın.
        Mesela !update done -> Daily'nin done bölümü güncellemek istiyorum.
        """
        print(ctx.author.display_name, 'update command start', now_time())

        if ctx.author == self.bot.user:
            return

        if not (ctx.channel.id == ctx.author.dm_channel.id):  # only dm
            return

        def check(author):
            def inner_check(ctx):
                return ctx.author == author
            return inner_check

        if (not arg) or (arg.lower() not in reaction.argumnat_list):
            await ctx.reply(
                f"Hatalı Arguman kullandınız. \n "
                f" --> **!update done**     - Daily done kısmını günceller  \n"
                f" --> **!update wip**      - Daily wip kısmını günceller \n"
                f" --> **!update blockers**   - Daily blockers kısmını günceller  \n"
                f" --> **!daily**                 - Tamamını günceller"
            )
            return

        try:
            await ctx.send(f"Daily'nin **{arg.upper()}** bölümünü nasıl güncellemek istersin?")
            msg = await self.bot.wait_for("message", timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return

            await ctx.channel.send("Güncellemeyi yapıyorum. Onaylıyormusun ? Y/N")
            is_okey = await self.bot.wait_for('message', timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(is_okey.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return

            if is_okey.content.lower() != 'y':
                await ctx.reply("Opps !! Birşeyler yanlış gitti sanırım :(")
                return

            data = mongo.daily_db.reports.find_and_modify(
                {"info.user_id": ctx.author.id,
                    "info.date": get_time()['date']},
                {"$set": {f"report.{arg}": msg.content}},
                new=True
            )

        except TimeoutError:
            await ctx.channel.send("Sizden istenen bilgiyi, Size ayrılan süre içerisinde giriniz.")
            return

        else:
            await self.bot.standup_channel.send(embed=create_embed(ctx, data['report'], reaction.update_title))
            await ctx.reply(f"Güncellemeyi yaptım. Daily raporunu yolluyorum :)")
            print(ctx.author.display_name, 'update command end', now_time())
            return

    @command(name='dailyall')
    async def reportall(self, ctx):
        """
        - Günlük Daily Raporunu tek seferde ekleyebilirsin. Daha önceden eklediysen tamamını güncelleyebilirsin.
        """
        print(ctx.author.display_name, 'dailyall command start', now_time())
        
        # await ctx.invoke(self.bot.get_command('tasks'))
        
        def check(author):
            def inner_check(ctx):
                return ctx.author == author
            return inner_check

        global daily_standup_channel, sample_standup
        if ctx.author == self.bot.user:
            return

        if not (ctx.channel.id == ctx.author.dm_channel.id):  # only dm
            return

        contains_done = False
        contains_wip = False
        contains_blockers = False

        standup = {"done": "", "wip": "", "blockers": ""}

        try:

            await ctx.send(reaction.standup_all_text.format(
                user=ctx.author.name, sample=reaction.sample_standup))
            msg = await self.bot.wait_for("message", timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- !daily veya !update komutu çalıştırıldı. Daily formatı uygun değil.")
                return

            parts = msg.content.split("#")
            for part in parts:
                if part.lower().startswith("done"):
                    print("done: OK")
                    standup["done"] = part[4:]
                    contains_done = True
                elif part.lower().startswith("wip"):
                    print("wip: OK")
                    standup["wip"] = part[3:]
                    contains_wip = True
                elif part.lower().startswith("blockers"):
                    print("blockers: OK")
                    standup["blockers"] = part[8:]
                    contains_blockers = True

            standup = fix_null_partition(standup)
            await ctx.channel.send(reaction.confirm_text.format(
                standup.get('done').strip(), standup.get('wip').strip(), standup.get('blockers').strip()))
            msg = await self.bot.wait_for('message', timeout=100.0, check=check(ctx.author))

            if not msg_is_suitable(msg.content):
                await ctx.reply("Opps -- Bir komut çalıştırıldı, lütfen tekrar deneyiniz.")
                return
            
            if msg.content.lower() != 'y':
                await ctx.reply("Opps !! Birşeyler yanlış gitti sanırım :(")
                return

        except TimeoutError:
            await ctx.reply("Sizden istenen bilgiyi, Size ayrılan süre içerisinde giriniz.")
            return
        else:
            if not (contains_done and contains_wip and contains_blockers):
                print("parsing error!", part)
                await ctx.reply(
                    f"hatali icerik! lutfen tekrar deneyin! mesaj icerisinde # karakteri kullanilamaz.\n\n{sample_standup}\n\n\n__hints__:\n\*\* bold\n\* italic\n\_\_ underline")
                return

        data = mongo.daily_db.reports.find_and_modify(
            {"info.user_id": ctx.author.id, "info.date": get_time()['date']},
            {"$set": build_structure(ctx.author, standup)},
            new=True)

        if data:
            await self.bot.standup_channel.send(embed=create_embed(ctx, data['report'], reaction.update_title))
            await ctx.channel.send(f"İyi Çalışmalar. Daily Raporunu güncelliyorum :)")
        else:
            mongo.daily_db.reports.insert(build_structure(ctx.author, standup))
            await self.bot.standup_channel.send(embed=create_embed(ctx, standup, reaction.info_title))
            await ctx.channel.send(f"İyi Çalışmalar. Daily Raporunu yolladım :)")
        
        print(ctx.author.display_name, 'dailyall command end', now_time())

    @command(name='weekly')
    async def weekly(self, ctx):
        """
        - Haftalık Rapor Özeti
        """
        print(ctx.author.display_name, 'weekly command start', now_time())
        
        if ctx.author == self.bot.user:
            return

        if not (ctx.channel.id == ctx.author.dm_channel.id):  # only dm
            return

        data, week_dates = get_weekly_data(ctx.author.id)
        print(ctx.author.name)
        await ctx.channel.send(
            file=File(fp=StringIO(reaction.html_table.format(
                data.to_html())), filename="weekly.html"),
            content=f"**{week_dates[0]}** - **{week_dates[-1]}**\nTarihleri Arasındaki Raporlarını Ekte Yolladım, bu hafta amma çok çalıştın :)")
        
        print(ctx.author.display_name, 'weekly command end', now_time())
        return

    @command(name='attendance', aliases=['yoklama', 'unreported'])
    async def attendance(self, ctx):
        '''
        Bu komutu kullanarak güncel rapor atmayanlar listesini görebilirsiniz
        '''
        print(ctx.author.display_name, 'attendance command start', now_time())
            
        task_members = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot == False and member not in task_members:
                    task_members.append(member)

        def get_unreported_list(reported):
            un_reported = []
            for user in task_members:
                if (user.id != self.bot.user.id) and (user.id not in settings.exclude_list) and (user.id not in reported):
                    un_reported.append(user.name)
            return un_reported

        reported = list_of_reports()
        un_reported = get_unreported_list(reported)
        await ctx.send(reaction.un_reported.format(get_time()['date'], len(un_reported), "\n- ".join(un_reported)))
        print(ctx.author.display_name, 'attendance command end', now_time())

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("daily")


def setup(bot):
    bot.add_cog(Daily(bot))
