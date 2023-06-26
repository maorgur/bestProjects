from datetime import datetime as dt
import time, requests
from threading import Thread
def MAtprint(*args, end = None, timestamp = False, program = True, webhook = True):
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
        tprint += 'DISCORD HoL matching'
    
    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:', *args, end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower MATHCING","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()

MAtprint('starting  matching...            ', end = '\r', webhook=False)
import random, hikari

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

def _matching_create_components(game_id = 0, user_id = 0, stop = False, bot = None, colors_selected = [None, None, None, None]):
    if stop:
        row = bot.rest.build_message_action_row()
        row.add_interactive_button(hikari.ButtonStyle.DANGER, f'matching stop {user_id} {game_id} other', label = 'stop game')
        return row
    #############
    rows = []
    for number in range(4):
        row = bot.rest.build_message_action_row()
        dropdown = row.add_text_menu(f'matching menu {user_id} {game_id} {number}', placeholder = f'choose color at position {number + 1}', max_values = 1, min_values = 1)
        for color in range(6):
            dropdown.add_option(f'{list(_matching_colors.keys())[color]}',f'matching play {user_id} {game_id} {number} {color}', description = f'set color to {list(_matching_colors.keys())[color]} at position {number + 1}', emoji = list(_matching_colors.values())[color], is_default = colors_selected[number] == color)
        rows.append(row)

    #####################################
    row = bot.rest.build_message_action_row()
    ###
    if not True in [colors_selected.count(color) > 1 for color in colors_selected] and not None in colors_selected: #not repeating, no unselected, valid
        button = row.add_interactive_button(hikari.ButtonStyle.SUCCESS, f'matching confirm {user_id} {game_id}', label = 'check', emoji = '✔️')
    elif None in colors_selected: #unselected
        row.add_interactive_button(hikari.ButtonStyle.SUCCESS, f'matching confirm {user_id} {game_id}', label = 'choose colors', emoji = '✖️', is_disabled = True)
    else: #repeating
        row.add_interactive_button(hikari.ButtonStyle.SUCCESS, f'matching confirm {user_id} {game_id}', label = 'colors cannot be repeated', emoji = '✖️', is_disabled = True)

    ###
    row.add_interactive_button(hikari.ButtonStyle.DANGER, f'matching stop {user_id} {game_id} same', label = 'stop game')

    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f'help matching', label = 'how to play', emoji = '📜')

    rows.append(row)
    ####################
    return rows

def check_result(target, to_check):
    result = []
    for color in range(len(to_check)):
        if to_check[color] == target[color]:
            result.append(True)
        elif to_check[color] in target:
            result.append(False)
        else:
            result.append(None)
    return result


_matching_colors = {'purple':'🟪', 'blue': '🟦', 'yellow': '🟨', 'green': '🟩', 'orange': '🟧', 'red': '🟥'}
matching_games = {}


async def matching_command(ctx, bot):
    global matching_games
    #check if game is active for the user
    if ctx.author.id in list(matching_games.keys()):
        await ctx.respond(embed = hikari.Embed(title = 'you have an active game going on', description='it looks like your\'re currently playing', color=(255,0, 0)).set_footer('if you can\'t continue the game, you can stop it'),component = _matching_create_components(matching_games[ctx.author.id]['game id'], ctx.author.id, True, bot = bot), flags = hikari.MessageFlag.URGENT)
        return

    game_id, sequence = ''.join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM', 5)), []
    for _ in range(4):
        x = random.randint(0,5)
        while x in sequence: x = random.randint(0,5)
        sequence.append(x)

    MAtprint(f'new game\tsequence: {"".join([list(_matching_colors.values())[color] for color in sequence])}\nuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)

    matching_games[ctx.author.id] = {'game id': game_id, 'sequence': sequence, 'past': [], 'selected': [None, None, None, None]}
    matching_games[ctx.author.id]['last response'] = time.time()
    message = await ctx.respond(content = f'❔ ❓ ❔ ❓\n{"⬇️ "*4}\n' + "\n".join(["🔳 " * 4 for _ in range(11)]), embed = hikari.Embed(title = 'solve the sequence', description = f'**try to find out whats the color sequence**\n*same color cannot appear twice*\nfor each color that in the sequence there will be ☑️\n**if it is in the same place in the sequence there will be ✅ instead**',color = (255, 255, 255)), components = _matching_create_components(game_id, ctx.author.id, bot = bot))
    matching_games[ctx.author.id]['message'] = message


async def matching_dropdown_update(event: hikari.InteractionCreateEvent, bot):
    if not isinstance(event.interaction, hikari.ComponentInteraction): return
    if event.interaction.component_type != hikari.ComponentType.TEXT_SELECT_MENU: return
    if not event.interaction.custom_id.startswith('matching menu'): return
    
    user_id, game_id, position, color = event.interaction.values[0].split()[2:]
    user_id, position, color = int(user_id), int(position), int(color)
    ############
    if not user_id in matching_games: #not playing
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content = '', embed=hikari.Embed(title = 'this game is not active anymore', color = (255, 0, 0)),components=[], attachments=[], flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif user_id != event.interaction.user.id:
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif matching_games[event.interaction.user.id]['game id'] != game_id: #not the active game (old game)
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='this is an old game',description='you have an active game, but it is not this!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    #######################

    matching_games[user_id]['selected'][position] = color

    selected = matching_games[user_id]['selected']

    content = f'❔ ❓ ❔ ❓\n{"⬇️ "*4}\n' #header
    for past in matching_games[user_id]['past']: #loop of past tries
        result = check_result(matching_games[user_id]["sequence"], past)
        content += ' '.join([list(_matching_colors.values())[color] for color in past]) + f'  {"✅" * result.count(True)}{"☑️" * result.count(False)}\n' #adds the past tries
    content += ' '.join([(list(_matching_colors.values()) + ['🔳'])[color] for color in [int(str(color).replace('None', '6')) for color in selected]]) + '\n' #adds the current line (with some list manipulation)
    content += "\n".join(["🔳 " * 4 for _ in range(11-len(matching_games[user_id]['past'])-1)]) #adds the rest blank tries

    matching_games[user_id]['last response'] = time.time()
    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content = content, embed = hikari.Embed(title = 'solve the sequence', description = f'**try to find out whats the color sequence**\n*same color cannot appear twice*\nfor each color that in the sequence there will be ☑️\n**if it is in the same place in the sequence there will be ✅ instead**',color = (255, 255, 255)), components = _matching_create_components(game_id, user_id, bot = bot, colors_selected=selected))


async def matching_game_update(event: hikari.InteractionCreateEvent, bot):
    global matching_games
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    
    if event.interaction.custom_id.startswith('matching stop'): #stop handle
        user_id, game_id, mode = event.interaction.custom_id.split()[2:]
        user_id = int(user_id)
        if mode == 'same': mode = hikari.ResponseType.MESSAGE_UPDATE
        else: mode = hikari.ResponseType.MESSAGE_CREATE


        #######
        if not user_id in matching_games: #not playing
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, content='', embed=hikari.Embed(title = 'this game is not active anymore', color = (255, 0, 0)),components=[], attachments=[], flags=hikari.MessageFlag.EPHEMERAL)
            return
        elif user_id != event.interaction.user.id:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        elif matching_games[event.interaction.user.id]['game id'] != game_id: #not the active game (old game)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, content = '', embed = hikari.Embed(title ='this is an old game',description='you have an active game, but it is not this!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return
        ####### stopping
        content = f'{" ".join([list(_matching_colors.values())[color] for color in matching_games[user_id]["sequence"]])}\n{"⬇️ "*4}\n' #header
        for past in matching_games[user_id]['past']: #loop of past tries
            result = check_result(matching_games[user_id]["sequence"], past)
            content += ' '.join([list(_matching_colors.values())[color] for color in past]) + f'  {"✅" * result.count(True)}{"☑️" * result.count(False)}\n' #adds the past tries
        content += "\n".join(["🔳 " * 4 for _ in range(11-len(matching_games[user_id]['past']))]) #adds the rest blank tries

        if mode == hikari.ResponseType.MESSAGE_UPDATE:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content=content, embed = hikari.Embed(title ='game stopped',color = (255, 255 , 0)), components = [create_help_component(bot)])
        else:
            
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title ='game stopped successfully',description=f'the sequence was ```{" ".join([list(_matching_colors.values())[color] for color in matching_games[user_id]["sequence"]])}```', color=(255, 255,0)), components=[])
            await matching_games[user_id]['message'].edit(content = content, embed = hikari.Embed(title ='game stopped', color = (255, 255 , 0)),components = [create_help_component(bot)])
        del matching_games[user_id]
        return
    #############################
    if not event.interaction.custom_id.startswith('matching confirm'): return
    ############################################################################

    user_id, game_id = event.interaction.custom_id.split()[2:]
    user_id = int(user_id)


    #######
    if not event.interaction.user.id in matching_games: #not playing
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='your\'e not playing', description = f'this is not your game! start your *own* game using </matching:{bot._slash_commands["matching"].instances[None].id}>!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    elif event.interaction.user.id != user_id: #not his game
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    elif matching_games[event.interaction.user.id]['game id'] != game_id: #not the active game (old game)
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='this is an old game',description='you have an active game, but it is not this!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    ####### play
    matching_games[user_id]['past'].append(matching_games[user_id]['selected'])
    matching_games[user_id]['last response'] = time.time()
    ######
    if matching_games[user_id]["sequence"] == matching_games[user_id]["selected"]: #win
        content = f'{" ".join([list(_matching_colors.values())[color] for color in matching_games[user_id]["sequence"]])}\n{"⬇️ "*4}\n' #header
        for past in matching_games[user_id]['past']: #loop of past tries
            result = check_result(matching_games[user_id]["sequence"], past)
            content += ' '.join([list(_matching_colors.values())[color] for color in past]) + f'  {"✅" * result.count(True)}{"☑️" * result.count(False)}\n' #adds the past tries
        content += "\n".join(["🔳 " * 4 for _ in range(11-len(matching_games[user_id]['past']))]) #adds the rest blank tries
        
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content = content, embed = hikari.Embed(title = '✅you won!✅', description = f'**you got the sequence in {len(matching_games[user_id]["past"])} tries!**',color = (0, 255, 0)), components = [])
        del matching_games[user_id]
        return
    ######
    if len(matching_games[user_id]['past']) >= 11:
        content = f'{" ".join([list(_matching_colors.values())[color] for color in matching_games[user_id]["sequence"]])}\n{"⬇️ "*4}\n' #header
        for past in matching_games[user_id]['past']: #loop of past tries
            result = check_result(matching_games[user_id]["sequence"], past)
            content += ' '.join([list(_matching_colors.values())[color] for color in past]) + f'  {"✅" * result.count(True)}{"☑️" * result.count(False)}\n' #adds the past tries
        content += "\n".join(["🔳 " * 4 for _ in range(11-len(matching_games[user_id]['past']))]) #adds the rest blank tries
        
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content = content, embed = hikari.Embed(title = '❌you lost❌', description = f'you failed to find sequence in 11 tries\n\ntry next time!',color = (255, 0, 0)), components = [])
        del matching_games[user_id]
        return
    #################

    matching_games[user_id]['selected'] = [None,None,None, None]
    content = f'❔ ❓ ❔ ❓\n{"⬇️ "*4}\n' #header
    for past in matching_games[user_id]['past']: #loop of past tries
        result = check_result(matching_games[user_id]["sequence"], past)
        content += ' '.join([list(_matching_colors.values())[color] for color in past]) + f'  {"✅" * result.count(True)}{"☑️" * result.count(False)}\n' #adds the past tries
    content += "\n".join(["🔳 " * 4 for _ in range(11-len(matching_games[user_id]['past']))]) #adds the rest blank tries

    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,content = content, embed = hikari.Embed(title = 'solve the sequence', description = f'**try to find out whats the color sequence**\n*same color cannot appear twice*\nfor each color that in the sequence there will be ☑️\n**if it is in the same place in the sequence there will be ✅ instead**',color = (255, 255, 255)), components = _matching_create_components(game_id, user_id, bot = bot, colors_selected=[None,None,None,None]))



    