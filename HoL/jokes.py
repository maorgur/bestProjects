from datetime import datetime as dt
import os, json, random
from threading import Thread
directory = os.path.dirname(os.path.realpath(__file__))

import requests
def JOtprint(*args, end = None, timestamp = False, program = True, webhook = True):
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
        tprint += 'DISCORD HoL jokes'
    
    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:', *args, end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower JOKES","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()

JOtprint('starting jokes...               ', end = '\r', webhook=False)
import hikari

with open(directory + '/HoL-jokes.json') as f:
    _jokes_command_list = json.load(f)

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

async def jokes_command(ctx, bot):
    JOtprint(f'sending {ctx.raw_options["type"]}\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    if ctx.raw_options['type'] == 'long joke':
        joke = random.choice(_jokes_command_list['long'])
        embed = hikari.Embed(title = 'joke about ' + joke['category'], description= joke['body'], url = 'https://github.com/taivop/joke-dataset/blob/master/stupidstuff.json', color = (0, 255, 255))
    elif ctx.raw_options['type'] == 'random thought / joke':
        joke = random.choice(_jokes_command_list['random'])
        embed = hikari.Embed(title = 'joke about ' + joke['title'], description= joke['body'], url = 'https://github.com/taivop/joke-dataset/blob/master/wocka.json', color = [random.randint(0, 255) for _ in range(3)]).set_footer('category: ' + joke['category'])
    elif ctx.raw_options['type'] == 'reddit joke':
        joke = random.choice(_jokes_command_list['reddit'])
        embed = hikari.Embed(title = joke['title'], description= joke['body'], url = 'https://github.com/taivop/joke-dataset/blob/master/reddit_jokes.json', color = (255, 100, 100)).set_footer(f'upvotes: {int(joke["score"])}')

    await ctx.respond(embed = embed, component = create_help_component(bot))