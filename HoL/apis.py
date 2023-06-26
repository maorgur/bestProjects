from datetime import datetime as dt
import os, json, random
from threading import Thread

directory = os.path.dirname(os.path.realpath(__file__))

import requests


def APItprint(*args, end=None, timestamp=False, program=True, webhook=True):
    '''tprints with file name and timestamp'''
    tprint = ''
    if timestamp:
        tprint += '.'.join([str(x) for x in dt.now().timetuple()[:3]])
        tprint += ' '
        tprint += ':'.join([str(x) for x in dt.now().timetuple()[4:7]])
        tprint = tprint[2:]  # remove the first digits of the year

    if timestamp and program:
        tprint += '  '  # space between sections

    if program:  # diffrent between programs
        tprint += 'DISCORD HoL bored'

    if tprint == None:  # for weird cases
        print(*args, end=end)
        return
    print(f'[{tprint}]:', *args, end=end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target=lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0',
                                            data={"content": payload_content, "embeds": None, "username": "Higher or Lower JOKES", "attachments": [],
                                                  "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()


APItprint('starting apies ⚙️...               ', end='\r', webhook=False)
import hikari
global bot

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label="view bot", emoji='👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label="main server", emoji='📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label="website", emoji='🌐')
    return row


async def bored_command(ctx, bot):
    if ctx.raw_options['type'] != None:
        APItprint(f'sending a {ctx.raw_options["type"]} activity\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
        await ctx.respond(f"# __finding something to do__\n### type: __**{ctx.raw_options['type']}**__")
    else:
        APItprint(f'sending an activity\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
        await ctx.respond(f"# __finding something to do__")
    # get activity
    if ctx.raw_options['type'] == None:
        activity = requests.get(f'https://www.boredapi.com/api/activity?minaccessibility=0&maxaccessibility=0.1&maxparticipants=1&maxprice=0.05').json()
    else:
        activity = requests.get(f'https://www.boredapi.com/api/activity?minaccessibility=0&maxaccessibility=0.15&maxparticipants=1&maxprice=0.1&type={ctx.raw_options["type"]}').json()

    embed = hikari.Embed(title="💭 activity to do", description=f'## {activity["activity"]}', color=(107, 163, 255))
    if activity["link"] != "":
        embed.add_field("🌐 link", "> " + activity["link"])
    embed.set_thumbnail("https://www.boredapi.com/favicon.ico")
    embed.set_footer(activity["type"])
    await ctx.edit_last_response(embed=embed, component=create_help_component(bot), content="")


async def tronald_dump_command(ctx, bot):
    APItprint(f'sending tronald dumb quote\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    await ctx.respond(content="# dumb quote that donald trump said")

    quote = requests.get("https://tronalddump.io/random/quote").json()
    embed = hikari.Embed(
        title=quote["value"],
        description=f'**[original tweet 🐦]({quote["_embedded"]["source"][0]["url"]})**',
        color=(243, 224, 125),
        timestamp=dt.strptime(quote["appeared_at"].replace("T", "-")[:-5], '%Y-%m-%d-%H:%M:%S').astimezone()
    )
    embed.set_footer("tronalddump.io")
    embed.set_thumbnail("https://www.tronalddump.io/img/tronalddump_850x850.png")

    await ctx.edit_last_response(embed=embed, component=create_help_component(bot))


async def advice_command(ctx, bot):
    APItprint(f'sending advice\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    await ctx.respond(content="# giving you a smart advice")
    advice = requests.get("https://api.adviceslip.com/advice").json()["slip"]["advice"]
    await ctx.edit_last_response(
        content="",
        embed=hikari.Embed(
            title=advice,
            color=(34, 152, 125),
            url="https://advicesslip.com"
        ).set_footer("adviceslip.com").set_thumbnail("https://adviceslip.com/app/img/favicon.ico"),
        component=create_help_component(bot))


async def chess_puzzle_command(ctx, bot):
    APItprint(f'sending a chess puzzle\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    await ctx.respond(content="# finding a chess puzzle for you...")
    puzzle = requests.get("https://api.chess.com/pub/puzzle/random").json()
    puzzle["pgn"] = puzzle["pgn"].replace("...", ".")
    if "#" in puzzle["pgn"]:
        description = f"checkmate in {puzzle['pgn'][puzzle['pgn'].find('1.'):].count('.')} moves"
    else:
        description = f"complete in {puzzle['pgn'][puzzle['pgn'].find('1.'):].count('.')} moves"
    await ctx.edit_last_response(content = "", component = create_help_component(bot),embed = hikari.Embed(
        title=puzzle["title"],
        description= f'## [click to solve the puzzle]({puzzle["url"]})\n\n' + description + f"\n\n**answer:** ||{puzzle['pgn'][puzzle['pgn'].find('1.'):-3]}||",
        color = (113, 140, 81),
        timestamp = dt.fromtimestamp(puzzle["publish_time"]).astimezone(),
        url = puzzle["url"]
    ).set_image(puzzle["image"]).set_thumbnail("https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/erik/phpwnLapM.png").set_footer("chess.com"))


async def chuck_norris(ctx, bot):
    APItprint(f'sending Chuck Norris sentence\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    await ctx.respond("# Chuck Norris once said")
    response = requests.get("https://api.chucknorris.io/jokes/random").json()
    await ctx.edit_last_response(content="", embed = hikari.Embed(title = response["value"], url = response["url"], color = (241, 90, 36)).set_footer("chucknorris.io").set_image("https://raw.githubusercontent.com/maorgur/external-files/main/ChuckNorris.gif"), component=create_help_component(bot))

