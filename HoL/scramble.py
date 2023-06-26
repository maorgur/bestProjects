from datetime import datetime as dt
import time, requests
from threading import Thread
def Stprint(*args, end = None, timestamp = False, program = True, webhook = True):
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
        tprint += 'DISCORD HoL scramble'
    
    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:', *args, end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower SCRAMBLE","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()

Stprint('starting scramble...         ',end = '\r', webhook = False)
import json,os,random
import hikari

#components
def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

def create_scramble_button_component(user_id, is_done = False, stop = False, bot=None):
    '''creats components for the game or stop button
    
    `user_id` necessery except from stop or is_done is true\n
    `is_done` will control if the guess button is disabled\n
    `stop` creates *only* stop button, parse as user id'''
    row = bot.rest.build_message_action_row()

    if user_id == None and isinstance(stop, int):
        row.add_interactive_button(hikari.ButtonStyle.DANGER, f'scramble-stop {stop} other', label = 'stop game') #stops the game and shows stopped response
        return row

    if not is_done:
        row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"scramble-guess {user_id}", label = 'guess ❓')
    else:
        row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"touch grass", label = 'guess ❓', is_disabled = True)
    if stop: #game is active
        row.add_interactive_button(hikari.ButtonStyle.DANGER, f'scramble-stop {user_id} same', label = 'stop game') #stops the game without stop response
    
    #how to play
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, 'help scramble', label = 'how to play', emoji = '📜')

    return row

def create_scramble_modal(user_id, bot=None):
    '''creats text prompt to guess the word using id
    
    returns title, description, and component'''
    global scramble_games
    word = scramble_games[user_id]['word']
    scramble = scramble_games[user_id]["scramble"]
    guess_count = scramble_games[user_id]['tries']


    row = bot.rest.build_modal_action_row()

    row.add_text_input(f'scramble-guess {user_id}', 'the scrambled word is '+ scramble, placeholder = f'the word is {len(word)} letters long. you have {guess_count} guesses remaining.', required = True, max_length = len(scramble), min_length = len(scramble), style = hikari.TextInputStyle.SHORT)

    #######
    description = f'what {scramble} actually means?, it is {len(word)} letters long'
    return '❔guess the word!❓', description, row


directory = os.path.dirname(os.path.realpath(__file__))

#load words.json
with open(f'{directory}/scramble-words.json') as f:
    words = [word for word in json.load(f) if len(word) >= 4 and len(word) < 7]

    
scramble_games = {}


async def scramble_command(ctx, bot):
    '''scramble initial command'''
    global scramble_games
    
    #check if game is active for the user
    if ctx.author.id in list(scramble_games.keys()):
        await ctx.respond(embed = hikari.Embed(title = 'you have an active game going on', description='it looks like your\'re currently playing', color=(255,0, 0)).set_footer('if you can\'t continue the game, you can stop it'),component = create_scramble_button_component(user_id = None, stop = ctx.author.id, bot=bot), flags = hikari.MessageFlag.URGENT)
        return

    word = 'FAILED TO LOAD'
    word = random.choice(words)

    game_id = ''.join(random.sample('QWERTYUIOPASDFGHJKLZXCVBNM1234567890', 5))
    scramble = ''.join(random.sample(word, len(word))).lower()

    while scramble == word: ''.join(random.sample(word, len(word))).lower() #prevents scrambled being the same

    scramble_games[ctx.user.id] = {'word': word.lower(),'scramble': scramble,'used letters': [], 'tries': 3, 'game id': game_id, 'last response': time.time()}

    Stprint(f'new game\t the word is {word} ({scramble})\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)

    message = await ctx.respond(embed = hikari.Embed(title = 'solve the word 🤔', description=f'the scrambled word is `{scramble}`', color=(0,255, 255)).set_footer(f'you have 3 tries remaining'),component=create_scramble_button_component(ctx.author.id, stop=True, bot=bot),flags = hikari.MessageFlag.URGENT)
    scramble_games[ctx.user.id]['message'] = message


async def scramble_update(event, bot):
    '''hikari.InteractionCreateEvent'''
    global scramble_games
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if  not event.interaction.custom_id.startswith('scramble'):
        return

    custom_id = event.interaction.custom_id[9:]

    if not custom_id.startswith('guess'):
        #stop
        
        if custom_id.startswith('stop'):
            user_id = int(custom_id.split()[1])

            if event.interaction.user.id != user_id:
                if user_id in list(scramble_games.keys()):
                    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'not your game',description='you have an active game, but not this', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)
                else:
                    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'not your game', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)

            else:
                if custom_id.split()[2] == 'other': await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title= 'stopped successfully',description=f'by the way the word was `{scramble_games[user_id]["word"]}`', color = (255, 255,0)),components=[], flags=hikari.MessageFlag.EPHEMERAL)
                else: await event.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)

                await scramble_games[user_id]['message'].edit(embed = hikari.Embed(title = 'stopped game', description=f'the scrambled word `{scramble_games[user_id]["scramble"]}` is **```{scramble_games[user_id]["word"]}```**', color = (255, 0,0)), components=[create_help_component(bot)])
                del scramble_games[user_id]
        return
    

    user_id = int(custom_id.split()[1])
    if event.interaction.user.id != user_id:
        if user_id in list(scramble_games.keys()):
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'not your game',description='you have an active game, but not this', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'not your game', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)

        return
    
    scramble_games[user_id]['last response']= time.time()
    await event.interaction.create_modal_response(*create_scramble_modal(user_id, bot=bot))

async def scramble_modal_response(event, bot):
    '''InteractionCreateEvent'''
    global scramble_games
    if not isinstance(event.interaction, hikari.ModalInteraction): return

    if not event.interaction.components[0].components[0].custom_id.startswith('scramble'):
        return
    

    user_id = int(event.interaction.components[0].components[0].custom_id.split()[1])

    if not user_id in list(scramble_games.keys()): #game inactive
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'game inactive', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)
        return

    if event.interaction.member.id != user_id: #not your game
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'not your\'e game',description=f'start a scramble game using </scramble:{bot._slash_commands["scramble"].instances[None].id}>', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    scramble_games[user_id]['last response']= time.time()
    value = event.interaction.components[0].components[0].value.lower()
    #check if valid key
    if False in [letter in 'qwertyuiopasdfghjklzxcvbnm' for letter in value]:
        try:#timeout
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title= 'invalid word',description='valid letters are **A-Z** and numbers', color = (255, 0,0)), flags=hikari.MessageFlag.EPHEMERAL)
        except (hikari.ForbiddenError, hikari.NotFoundError): pass #
        return

    #game processing
    word = scramble_games[user_id]['word'].lower().strip()
    scramble = scramble_games[user_id]['scramble'].lower().strip()
    
    #check if winning
    if word == value: #true if won
        try: #timeout
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title= 'you won! 🥳',description=f'the word was\n`{scramble_games[user_id]["word"]}`!\n\nyou guessed in **{4-scramble_games[user_id]["tries"]} tries**!', color = (0, 255,0)),components=[create_scramble_button_component(user_id, True, bot=bot)], flags=hikari.MessageFlag.URGENT)
        except: return
        del scramble_games[user_id]
        return

    #check if losing
    if not value in word and scramble_games[user_id]['tries'] <= 1:
        try:
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title= 'you lost! 😞',description=f'the word was\n`{scramble_games[user_id]["word"]}`\n\nplay again!', color = (255, 0,0)),components=[create_scramble_button_component(user_id, True, bot=bot), create_help_component(bot)], flags=hikari.MessageFlag.URGENT)
        except (hikari.ForbiddenError, hikari.NotFoundError): return
        del scramble_games[user_id]
        return


    #respond
    try:
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title= '❌ incorrect ❌',description=f'`{value}` is **not** the word ❌\n\nthe scrambled word is {scramble}', color = (255, 255,0)).set_footer(f'you have {scramble_games[user_id]["tries"]-1} tries remaining'),component=create_scramble_button_component(user_id, stop=True, bot=bot), flags=hikari.MessageFlag.URGENT)
        scramble_games[user_id]["tries"] -= 1
    except (hikari.ForbiddenError, hikari.NotFoundError): return
