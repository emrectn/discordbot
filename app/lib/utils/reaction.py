
class Reaction:
    argumnat_list = ["done", "wip", "blockers"]

    standup_replies = [
        "Heyyyyoo {}!",
        "Yuppii {}! ",
        "Çok Teşekkürler {}",
        "Harikasın {}!",
    ]

    standup_text = "Merhaba {user}, bugün neler yaptığını paylaşmaya hazır mısın?\nDaily için **!daily** veya **!dailyall** komutunu yazman yeterli."
    standup_all_text = "Merhaba {user}, bugün neler yaptığını paylaşmaya hazır mısın?\n\n**Sample**:\n\n{sample}"
    sample_standup = "#done\ngpu limitleme calismasi\nicerik sınıflandırma model egitimi\nx proje toplantisi\n\n#wip\nY v1.0 code review\nz project sync toplantisi\ncrm entegrasyon gelistirmeleri\n\n#blockers\n123 nolu fw talebi\n456 nolu kurulum cagrisi\ncitrix erisim problemi"

    confirm_text = "**#done**\n{}\n\n**#wip**\n{}\n\n**#blockers**\n{}\n\n**Daily Raporunu yolluyorum. Onaylıyormusun ? Y/N**"
    info_title = "Daily Raporu Tamamlandı!"
    update_title = "Daily Raporu Güncellendi!"
    info_text_desc = "Teşekkürler **{user}**!"

    un_reported = "**Tarih: {} - Rapor Yollamayan Kişi Sayısı: {}** \nRapor Yollamayanların Listesi ->\n------------------------------------------\n- {}"

    html_table = """\
        <html>
        <head></head>
        <body>
            {}
        </body>
        </html>
        """



reaction = Reaction()