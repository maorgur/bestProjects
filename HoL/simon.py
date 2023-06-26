import asyncio, time, requests
from datetime import datetime as dt
from threading import Thread
def SItprint(*args, end = None, timestamp = False, program = True, webhook = True):
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
        tprint += 'DISCORD HoL simon'
    if tprint == '': #for weird cases
        print(*args, end = end)
        return
    print('[{tprint}]:', *args, end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower SIMON","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()

SItprint('starting simon...            ', end = '\r', webhook=False)
import os,random,sys, io, hikari
from PIL import Image, ImageDraw, ImageFont


dir_path = os.path.dirname(os.path.realpath(__file__))
dir_slash = '\\' if 'win' in sys.platform.lower() else '/'

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

_simon_font = ImageFont.truetype(font=f"{dir_path}{dir_slash}font.ttf", size=100)

_simon_colors = {'purple':'🟪', 'grey': '🔳', 'blue': '🟦', 'yellow': '🟨', 'green': '🟩', 'orange': '🟧', 'cyan': '🔵', 'pink': '🟣', 'red': '🟥'}


def _simon_create_components(game_id = 0, user_id = 0, stop = False, bot = None):
    if stop:
        row = bot.rest.build_message_action_row()
        row.add_interactive_button(hikari.ButtonStyle.DANGER, f'simon stop {user_id} {game_id} other', label = 'stop game')
        return row
    #############
    rows = []
    for index_row in range(3):
        row = bot.rest.build_message_action_row()
        for color in range(index_row*3,index_row*3 + 3):
            row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f'simon play {list(_simon_colors.keys())[color]} {user_id} {game_id}', label = list(_simon_colors.values())[color])
        rows.append(row)


    row = bot.rest.build_message_action_row() #stop and how to play
    row.add_interactive_button(hikari.ButtonStyle.DANGER, f'simon stop {user_id} {game_id} same', label = 'stop game')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f'help simon', label = 'how to play', emoji = '📜')

    rows.append(row)
    ####################
    return rows

def _simon_write_Text(image, text, coords):
    global _simon_font
    '''writes the text to the image'''

    draw_img = image.copy()
    draw = ImageDraw.Draw(draw_img)
    draw.text(coords, text, font=_simon_font, fill='white', align='center', anchor='mm')

    return draw_img

def _simon_create_image(selected = None):
    img = Image.new('RGB', (300, 300), 'black')
    load = img.load()

    rgb_values = [
        (255, 0, 255),
        (171, 178, 224),
        (0, 0, 255), #blue
        (255, 255, 0), #yellow
        (0, 255, 0), #green
        (255, 128, 0), #orange
        (0, 255, 255), #cyan
        (255, 192, 203),
        (255, 0, 0) #red
        ]

    for color in range(9):
        if color != selected:
            rgb_values[color] = tuple([int(channel//2) for channel in rgb_values[color]])

    for x in range(300):
        for y in range(300):
            if y < 100:
                if x < 100:load[x,y] = rgb_values[0]
                elif x < 200:load[x,y] = rgb_values[1]
                else:load[x,y] = rgb_values[2]
            elif y < 200:
                if x < 100:load[x,y] = rgb_values[3]
                elif x < 200:load[x,y] = rgb_values[4]
                else:load[x,y] = rgb_values[5]
            else:
                if x < 100:load[x,y] = rgb_values[6]
                elif x < 200:load[x,y] = rgb_values[7]
                else:load[x,y] = rgb_values[8]
    return img

def _simon_create_gif(colors = [0,1,2,3,4,5,6,7,8]):
    '''creats gif for the game\n
    `colors` sequence of the colors numbers\n
    returns `BytesIO` of the gif'''
    img = _simon_create_image()
    imgs = [_simon_write_Text(img, '3', (150, 150)), _simon_write_Text(img, '2', (150, 150)), _simon_write_Text(img, '1', (150, 150)), img]
    imgs = [elem for pair in zip(imgs, imgs) for elem in pair]

    for color in colors:
        imgs.append(_simon_create_image(color))
        imgs.append(_simon_create_image())

    for _ in range(20): imgs.append(_simon_create_image())

    buffer = io.BytesIO()
    imgs[0].save(buffer,format='GIF', append_images = imgs[1:],optimize=False, duration = 500, loop = 1, save_all=True)
    return buffer, len(imgs)//2 -9 + (len(colors) * 0.15) #time: the length of the images divided because of duration minus end buffer plus *loading time* - it takes some time to discord client to load long gifs


def _simon_single_image_to_bytes(color_index = None):
    buf = io.BytesIO()
    _simon_create_image(color_index).save(buf, 'JPEG', quality = 70)
    return hikari.files.Bytes(buf.getvalue(), 'simon game.jpg')
simon_games = {}


async def simon_command(ctx, bot):
    global simon_games
    #check if game is active for the user
    if ctx.author.id in list(simon_games.keys()):
        await ctx.respond(embed = hikari.Embed(title = 'you have an active game going on', description='it looks like your\'re currently playing', color=(255,0, 0)).set_footer('if you can\'t continue the game, you can stop it'),component = _simon_create_components(simon_games[ctx.author.id]['game id'], ctx.author.id, True, bot), flags = hikari.MessageFlag.URGENT)
        return

    SItprint(f'new game\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)
    message = await ctx.respond(embed = hikari.Embed(title='creating game...', color = (0, 255, 0)))
    game_id, sequence = ''.join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM', 5)), [random.randint(1,8) for _ in range(3)]
    simon_games[ctx.author.id] = {'game id': game_id, 'sequence': sequence, 'message': message, 'is showing': True}
    gif, length_of_gif = _simon_create_gif(sequence)
    simon_games[ctx.author.id]['last response'] = time.time() + length_of_gif + 3
    await ctx.edit_last_response(embed = hikari.Embed(title = 'remember the sequence!', description = 'look an the GIF, remember this 3 moves',color = (255, 255, 255)).set_footer('this will not be repeated!').set_image(hikari.files.Bytes(gif.getvalue(), 'simon game, remember this.gif')))
    del gif
    await asyncio.sleep(length_of_gif+0.5)
    await ctx.edit_last_response(content = '❔❔❔', embed = hikari.Embed(title = 'what is the sequence?', color = (255, 255, 0)).set_footer(f'repeat 3 moves!').set_image(_simon_single_image_to_bytes()), components = _simon_create_components(game_id, ctx.author.id, bot = bot))
    simon_games[ctx.author.id]['is showing'] = False
    simon_games[ctx.author.id]['repeating'] = 0 #number of tile that repeated


async def simon_game_update(event: hikari.InteractionCreateEvent, bot):
    global simon_games

    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if not event.interaction.custom_id.startswith('simon'): return
    
    if event.interaction.custom_id.startswith('simon stop'): #stop handle
        user_id, game_id, mode = event.interaction.custom_id.split()[2:]
        user_id = int(user_id)
        if mode == 'same': mode = hikari.ResponseType.MESSAGE_UPDATE
        else: mode = hikari.ResponseType.MESSAGE_CREATE


        #######
        if not user_id in simon_games: #not playing
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title = 'this game is not active anymore', color = (255, 0, 0)),components=[], attachments=[], flags=hikari.MessageFlag.EPHEMERAL)
            return
        elif user_id != event.interaction.user.id:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        elif simon_games[event.interaction.user.id]['game id'] != game_id: #not the active game (old game)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='this is an old game',description='you have an active game, but it is not this!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        elif simon_games[event.interaction.user.id]['is showing']: #showing sequence
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title ='cannot stop game now',description='you cannot stop a game while showing the sequence, please wait', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        #######
        if mode == hikari.ResponseType.MESSAGE_UPDATE:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title ='game stopped',description=f'**your\'e score is** `{len(simon_games[user_id]["sequence"])-3}`. \n\nthe sequence was ```{", ".join([list(_simon_colors.keys())[color] for color in simon_games[user_id]["sequence"]])}```', color = (255, 255 , 0)).set_image(_simon_single_image_to_bytes()),components = [create_help_component(bot)])
        else:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title ='game stopped successfully', description=f'**your\'e score is** `{len(simon_games[user_id]["sequence"])-3}`. \n\nthe sequence was ```{", ".join([list(_simon_colors.keys())[color] for color in simon_games[user_id]["sequence"]])}```', color=(255, 255,0)), components=[])
            await simon_games[user_id]['message'].edit(embed = hikari.Embed(title ='game stopped',description=f'**your\'e score is** `{len(simon_games[user_id]["sequence"])-3}`. \n\nthe sequence was ```{", ".join([list(_simon_colors.keys())[color] for color in simon_games[user_id]["sequence"]])}```', color = (255, 255 , 0)).set_image(_simon_single_image_to_bytes()),components = [create_help_component(bot)])
        del simon_games[user_id]
        return
    ############################################################################

    color, user_id, game_id = event.interaction.custom_id.split()[2:]
    user_id = int(user_id)
    color = list(_simon_colors.keys()).index(color)


    #######
    if not event.interaction.user.id in simon_games: #not playing
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='your\'e not playing', description = f'this is not your game! start your *own* game using </simon:{bot._slash_commands["simon"].instances[None].id}>!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    elif event.interaction.user.id != user_id: #not his game
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    elif simon_games[event.interaction.user.id]['game id'] != game_id: #not the active game (old game)
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='this is an old game',description='you have an active game, but it is not this!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    #######

    if color != simon_games[user_id]['sequence'][simon_games[user_id]['repeating']]:
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title ='you failed!',description=f'**your\'e score is** `{len(simon_games[user_id]["sequence"])-3}`. \n\nthe sequence was ```{", ".join([list(_simon_colors.keys())[color] for color in simon_games[user_id]["sequence"]])}```', color = (255, 0 , 0)).set_image(_simon_single_image_to_bytes()),components = [create_help_component(bot)])
        del simon_games[user_id]
        return
    
    else: #correct
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, content = ''.join([list(_simon_colors.values())[color] for color in simon_games[user_id]["sequence"][:simon_games[user_id]["repeating"]+1]]) + f'{(len(simon_games[user_id]["sequence"]) - simon_games[user_id]["repeating"] -1) * "❔"}', embed = hikari.Embed(title ='✅correct ✅',description=f'complete the round!', color = (0, 255, 0)).set_footer(f'repeat {len(simon_games[user_id]["sequence"]) - simon_games[user_id]["repeating"] -1} moves!').set_image(_simon_single_image_to_bytes(color)), components=([_simon_create_components(game_id, user_id, bot = bot) for _ in range(1) if simon_games[user_id]['repeating']+1 != len(simon_games[user_id]['sequence'])] + [None])[0],flags=hikari.MessageFlag.EPHEMERAL)
        simon_games[user_id]['repeating'] += 1
        simon_games[user_id]['last response'] = time.time() + 4
        ##############################
        if simon_games[user_id]['repeating'] == len(simon_games[user_id]['sequence']):

            simon_games[user_id]['sequence'].append(random.randint(0,8))
            simon_games[user_id]['is showing'] = True
            gif, gif_time = _simon_create_gif(simon_games[user_id]['sequence'])
            simon_games[user_id]['last response'] = time.time() + gif_time + 1.5
            await event.interaction.edit_initial_response(content = None, embed = hikari.Embed(title = 'remember the sequence!', description = f'look an the GIF, remember this {len(simon_games[user_id]["sequence"])} moves',color = (255, 255, 255)).set_footer('this will not be repeated!').set_image(hikari.files.Bytes(gif.getvalue(), 'simon game, remember this.gif')), components=[])
            del gif
            await asyncio.sleep(gif_time)
            await event.interaction.edit_initial_response(content = '❔❔❔', embed = hikari.Embed(title = 'what is the sequence?', color = (255, 255, 0)).set_footer(f'repeat {len(simon_games[user_id]["sequence"])} moves!').set_image(_simon_single_image_to_bytes()), components = _simon_create_components(game_id, user_id, bot = bot))
            simon_games[user_id]['is showing'] = False
            simon_games[user_id]['repeating'] = 0