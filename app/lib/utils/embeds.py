from discord import Embed
from lib.utils.reaction import reaction


def create_embed(ctx, standup, title):
    pfp = ctx.author.avatar_url
    embedVar = Embed(title=title,
                     description=reaction.info_text_desc.format(
                         user=ctx.author.mention),
                     color=0x00ff00)
    embedVar.set_thumbnail(url=(pfp))
    embedVar.add_field(name="#done", value=standup.get(
        "done", ""), inline=False)
    embedVar.add_field(name="#wip", value=standup.get("wip", ""), inline=False)
    embedVar.add_field(name="#blockers", value=standup.get(
        "blockers", ""), inline=False)

    return embedVar
