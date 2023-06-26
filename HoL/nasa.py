from datetime import datetime as dt
import os, json, random
from datetime import timedelta
from threading import Thread
directory = os.path.dirname(os.path.realpath(__file__))

import requests
def ntprint(*args, end = None, timestamp = False, program = True, webhook = True):
    '''tprints with file name and timestamp'''
    tprint = ''
    if timestamp:
        tprint += '.'.join([str(x) for x in dt.now().timetuple()[:3]])
        tprint += ' '
        tprint += ':'.join([str(x) for x in dt.now().timetuple()[4:7]])
        tprint = tprint[2:] #remove the first digits of the year

    if timestamp and program:
        tprint += '  ' #space between sections

    if program: #diffrent between programs
        tprint += 'DISCORD HoL nasa'

    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:', *args, end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower JOKES","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()

ntprint('starting nasa 🛰️...               ', end = '\r', webhook=False)
import hikari

apiKey = "VpRuTCediCfVsOFXgspcrXZIgMoZ0ndayrxcDMOU"
def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

async def apod_command(ctx, bot):
    #calculate date
    date = dt.utcnow()
    if (ctx.raw_options['days-back'] != None):
        date = date - timedelta(ctx.raw_options['days-back'])
    ntprint(f'sending APOD of {date}\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)

    await ctx.respond(f"# loading the __Astronomy Picture of the Day__\n### date: {date.year}-{date.month}-{date.day}")
    #get image data
    data = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={apiKey}&thumbs=true&date={date.year}-{date.month}-{date.day}').json()
    data["explanation"] = " - " + data["explanation"].replace(".", ".\n - ")

    embed = hikari.Embed(title="🛰️Astronomy Picture of the Day🚀", description=f'# {data["title"]}\n{data["explanation"]}', color = (12, 19, 79), url = "https://apod.nasa.gov/apod/astropix.html")
    embed.set_footer(f'{date.year}-{date.month}-{date.day}')
    if data["media_type"] == 'image':
        try:
            embed.set_image(data["hdurl"])
        except KeyError:
            embed.set_image(data["url"])
    else: #video
        embed.set_image(data["thumbnail_url"])
    embed.set_thumbnail("https://api.nasa.gov/assets/img/favicons/favicon-192.png")
    if data["media_type"] == "video":
        await ctx.edit_last_response(embed=embed, component=create_help_component(bot), content=data["url"])
    else:
        await ctx.edit_last_response(embed = embed, component = create_help_component(bot), content = "")

async def rover_command(ctx, bot):
    availableCameras = {
        "curiosity": ["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM"],
        "opportunity": ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"],
        "spirit": ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"],
    }