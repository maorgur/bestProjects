import hikari, asyncio, requests, time, random, sys, json, os
from datetime import datetime as dt
from threading import Thread
from PIL import Image
from io import BytesIO
def Htprint(*args, end = None, timestamp = False, program = True, webhook = True, color = None):
    '''tprints with file name and timestamp'''
    tprint = ''
    if timestamp:
        tprint += '.'.join([str(x) for x in dt.now().timetuple()[:3]]) #date
        tprint += ' '
        tprint += ':'.join([str(x) for x in dt.now().timetuple()[4:7]]) #time
        tprint = tprint[2:] #remove the first digits of the year

    if timestamp and program:
        tprint += '  ' #space between sections

    if program: #diffrent between programs
        tprint += 'DISCORD HoL HoL'
    
    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:' + ''.join([f"\033[38;2;{color[0]};{color[1]};{color[2]}m" for _ in range(1) if color != None]), *args,'\033[0m', end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower HoL","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()


hol_games = {} #user.id = {score, last_data = {name, image, number}}
hol_play_settings = {}

async def send_DM(bot, user, embed = None, content = None, component = None):
    try:
        await (await bot.rest.create_dm_channel(int(user))).send(embed = embed, content = content, component=component)
        return True
    except Exception as e:
        return False
    
#get list functions
def is_valid(name):
    """makes sure name is SFW and not a question"""
    invalid_keywords = ['ajva','fabswingers','literot', 'anerucab exoress', 'antera vasna', 'music and arts', 'brazzer', 'redtube', 'art lingerie', 'chaturbate', 'erotic 3d', 'seduc', 'cam4', 'xxx', 'sex', 'naked', 'porn', 'nud', 'dick', 'how', 'what', 'who', 'why']
    for filter in invalid_keywords:
        if filter in name.lower() or name.lower().startswith('x') or name.lower().startswith('can ') or name.lower().startswith('is '):
            return False
    return True

def filter_value_multi(dictonary, max_len = 100):
    """loop of filter_value and is_valid and max length option"""
    safe_dict = {}
    for key, value in dictonary.items():
        if is_valid(key) and len(key) < max_len and random.randint(1, 75_000) < value:
            safe_dict[key] = value
    return safe_dict

def get_list():
    '''scrape list of words from mondovo.com'''
    urls = ['https://mondovo.com/keywords/most-searched-words-on-google/',  'https://mondovo.com/keywords/photography-keywords', 'https://mondovo.com/keywords/art-keywords', 'https://mondovo.com/keywords/travel-keywords', 'https://mondovo.com/keywords/computer-keywords', 'https://mondovo.com/keywords/music-keywords', 'https://mondovo.com/keywords/education-keywords']
    result = {}
    for url in urls:
        Htprint('Getting list from ' + url)
        text = requests.get(url, headers={'User-Agent': 'discord Higher or Lower bot/1.0 (https://maorgur500.wixsite.com/drife-bots/; https://discord.gg/P5dYvqcexf) hikari python/2.0.0.dev116'}).text #wikipedia wants this
        s = text.split('<td>')

        for line in range(len(s)):
            if s[line][0].isalpha() and not 'ref="' in s[line] and is_valid(s[line]):
                result[s[line][0:s[line].find('</td>')]] =  int(s[line+1][:s[line+1].find('</td>')].replace(',', ''))
    Htprint('Got list')
    return result

#load words.json
directory = os.path.dirname(os.path.realpath(__file__))
try:
    with open(f'{directory}/words.json', 'r') as f: words = json.load(f)
    Htprint('total keywords:', len(words), end = '\t')
    words = filter_value_multi(words, 30)
    Htprint('after filter:', len(words))
except:
    words = get_list()
    Htprint('new list: ', len(words))
    with open(f'{directory}/words.json', 'w') as f: json.dump(words, f, indent = 4)
    words = filter_value_multi(words, 30)
    Htprint('after filter:', len(words))

#load urls.json
try:
    with open(f'{directory}/urls.json', 'r') as f: image_urls = json.load(f)
    Htprint(len(image_urls), 'image urls loaded')
    google_scrape, pixabay, duckduckgo = 0, 0, 0
except:
    image_urls = {}
    Htprint('0 image urls loaded')
    with open(f'{directory}/urls.json', 'w') as f: json.dump(image_urls, f)



#image processing
def search_for_image(query):
    global image_urls
    query = query.replace(' ', '+')
    if query in image_urls:
        if image_urls[query] == 'pixabay':
            try:
                urls = requests.get(f'https://pixabay.com/api/?key=29800473-2266f7eb9aaeae678c8696ef5&q={query}&safe_search=true&per_page=3').json()
                urls['hits'][0]['webformatURL'] #will raise an error if not found
                return urls['hits'][0]['webformatURL']
            except:
                del image_urls[query]
        elif not 'gstatic' in image_urls[query]:
                return image_urls[query]

    #duckduckgo 
    try:
        response = requests.get(f'https://duckduckgo.com/?q={query}&format=json').json()
        result = 'https://duckduckgo.com' + response['RelatedTopics'][0]['Icon']['URL']
    except:
       pass
    else:
        if '/i/' in result:
            image_urls[query] = result
            return result

    #pixabay
    try:
        urls = requests.get(f'https://pixabay.com/api/?key=29800473-2266f7eb9aaeae678c8696ef5&q={query}&safe_search=true&per_page=3').json()
        urls['hits'][0]['webformatURL'] #will raise an error if not found
        image_urls[query] = 'pixabay'
        return urls['hits'][0]['webformatURL']
    except:
        pass


    if query in image_urls:
        return image_urls[query]
    #google scrape
    try:
        data = requests.get(f'https://google.com/search?q={query}&tbm=isch&tbs=isz:l&hl=iw&sa=X&ved=0CAIQpwVqFwoTCKjz3Le9-fkCFQAAAAAdAAAAABAC&biw=1277&bih=636').text
        for i in range(len(data) - 10):
            current_url = ''
            if i == len(data) - 10:
                pass
            elif data[i: i+4] == 'src=':
                x = i +5
                current_url = ''
                while not data[x] == '"':
                    current_url += data[x]
                    x+=1
                if 'http' in current_url:
                    image_urls[query] = current_url
                    return current_url
    except:
        pass

def get_image_from_url(url, fallback_value):
    '''value is there to try again if fails to get image'''
    global image_urls
    for _ in range(3):
        try:
            response = requests.get(url)
            return Image.open(BytesIO(response.content))
        except Exception as e:
            if response.status_code != 400: #pixabay old
                Htprint('got an error while getting image:', e, response.status_code, response.reason)

        try: #get new image if got an error
            url = search_for_image(fallback_value)
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            image_urls[fallback_value.replace(' ', '+')] = url
            return img
        except:
            Htprint(f'failed to get fallback image for {url}')

        return Image.new('RGB', (300, 100), color = (150, 150, 150))

def get_images(l, word1 = None, word2 = None, img1 = None, img2 = None):
    '''choose, get link, load images'''
    if word1 == None:
        word1 = random.choice(list(l.keys()))
    if word2 == None:
        word2 = random.choice(list(l.keys()))
        while word2 == word1:
            word2 = random.choice(list(l.keys()))
    
    if img1 == None:
        img1 = get_image_from_url(search_for_image(word1), word1)
    if img2 == None:
        img2 = get_image_from_url(search_for_image(word2), word2)
    #create big image with the first word on top and the second word on bottom
    width = max([img1.width, img2.width])
    img1 = resize_image(img1, width)
    img2 = resize_image(img2, width)
    img = Image.new('RGBA', (width, img1.height + img2.height + 10), (255, 255, 255, 0))
    img.paste(img1, (0, 0))
    img.paste(img2, (0, img1.height + 10))

    return {'big image': img, 'words': [word1, word2], 'images': [img1, img2], 'values': [l[word1], l[word2]]}

def resize_image(img, width):
    '''resize image without changing ratio
    also diffrent code to linux and windows to stop warning'''
    wpercent = (width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    if 'win' in sys.platform:
        return img.resize((width, hsize), Image.Resampling.LANCZOS) #stop warnings
    else:
        return img.resize((width, hsize), Image.LANCZOS) #stop warnings

#component
def HoL_create_component(bot, user_id, disabled = False, report_disabled = False, game_id = 0, selected_button = None, only_stop = False):
    '''creats row of higher or lower compnents (and report button)'''
    row = bot.rest.build_message_action_row()
    row.add_interactive_button(hikari.ButtonStyle.SUCCESS, f"HoL h {user_id} {game_id}", label = 'higher',
                                        is_disabled=(selected_button == None or selected_button == 'l') and disabled)
    
    row.add_interactive_button(hikari.ButtonStyle.DANGER, f"HoL l {user_id} {game_id}", label = "lower",
                               is_disabled = (selected_button == None or selected_button == 'h') and disabled)
    
    row.add_interactive_button(hikari.ButtonStyle.SECONDARY, 'HoL report', label='report', emoji = '🚩', is_disabled=report_disabled)

    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, 'help HoL', label='how to play', emoji = '📜')


    #stop button
    if not disabled and not report_disabled and selected_button == None:
        if only_stop:
            row = bot.rest.build_message_action_row()
            row.add_interactive_button(hikari.ButtonStyle.DANGER, f'HoL stop {user_id} {game_id} other', label = 'stop game', emoji = '🛑')
        else:
            row.add_interactive_button(hikari.ButtonStyle.DANGER, f'HoL stop {user_id} {game_id} same', label = 'stop game', emoji = '🛑')


    return row

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label = "view bot", emoji = '👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

async def HoL_command(ctx, bot):
    global hol_games, hol_play_settings
    try:
        user_id = ctx.author.id
        if user_id in hol_games:
            await ctx.respond(embed = hikari.Embed(title = 'already in a game', color = (255, 0, 0)),component = HoL_create_component(bot, user_id, game_id = hol_games[user_id]['game id'], only_stop=True) ,flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        if not str(user_id) in hol_play_settings: #update play settings
            hol_play_settings[str(user_id)] = 0

        #starts game
        Htprint(f'new game\tuser: {ctx.author.username}\t@{ctx.author.global_name} {ctx.author.id}', timestamp=True)

        message = await ctx.respond(hikari.Embed(title = 'play', description = f':hourglass_flowing_sand: loading images!... :hourglass_flowing_sand:\n\nthis is your *{hol_play_settings[str(user_id)] + 1}* game today!', color = (255, 255, 0)).set_footer('starting your game, may take few seconds...'), reply = True, flags = hikari.MessageFlag.LOADING)
        hol_play_settings[str(user_id)] += 1
        hol_games[user_id] = {'is loading': True, 'game id': -1, 'last response': time.time()}
        images_data = await asyncio.get_running_loop().run_in_executor(bot.executor, lambda: get_images(words))
        embed_to_send = hikari.Embed(title = 'higher or lower?', description =  f':arrow_up:**`{images_data["words"][0]}`**:arrow_up: - ***{images_data["values"][0]:,}* searches**  - (`higher`)\n\n :arrow_down:**`{images_data["words"][1]}`**:arrow_down: - ***???* searches** - (`lower`)', color = (0, 0, 0))
        #save image
        buf = BytesIO()
        images_data['big image'].save(buf, format = 'PNG')
        embed_to_send.set_footer(f'score: 0')
        game_id = random.randint(1, 9999999)
        row = HoL_create_component(bot, user_id, game_id = game_id)
        await ctx.edit_last_response(content = f'**we added alot more games!\ncheck them out in** </help:{bot._slash_commands["help"].instances[None].id}>!',embed = embed_to_send, component = row, attachment = hikari.files.Bytes(buf.getvalue(), 'which-one-is-higher.png'))
        del hol_games[user_id]
        hol_games[user_id] = {'score' : 0, 'data' : images_data, 'game id': game_id,'message' : message,'message embed': embed_to_send, 'is loading': False, 'last response': time.time()}


    except hikari.errors.NotFoundError:
        if user_id in hol_games: #cannot update response (user deleted message?)
            del hol_games[user_id]
            await send_DM(bot, int(user_id), embed = hikari.Embed(title = 'it looks like your\'e *Higher or Lower* game was deleted', description='for unknown reason, the game cannot start\n\ntry playing here in the DM where there are no interruptions', color = (255, 0,0)))
    
    except hikari.errors.ForbiddenError:
        Htprint('got forbidden error while trying to start a game')
        if user_id in hol_games:
            del hol_games[user_id]
        hol_play_settings[str(user_id)] -= 1
        await ctx.respond(embed = hikari.Embed(title = 'unable to start a game',description = 'it looks like **Higher or Lower** doesn\'t have permission to start a game in this channel', color = (255, 0, 0)), flags=hikari.MessageFlag.EPHEMERAL)
    
    except Exception as e:
        Htprint('got an error while trying to start a game', e)
        if user_id in hol_games:
            del hol_games[user_id]
        hol_play_settings[str(user_id)] -= 1
        await ctx.respond(embed = hikari.Embed(title = 'falied to load',description = f'got an error while stopping a game\n if this error keeps occurring, create a ticket in the support server', color = (255, 0, 0)), flags=hikari.MessageFlag.EPHEMERAL)

async def HoL_update(event, bot):
    global hol_games, image_urls
    added = False
    # Filter out all unwanted interactions
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return
    if event.interaction.custom_id == 'HoL report' or event.interaction.custom_id.startswith('help'): return
    if not event.interaction.custom_id.startswith('HoL'): return
    
    data = event.interaction.custom_id[4:]

    if data.startswith('stop'): #stop game
        game_user_id = int(data.split()[1])
        game_id = int(data.split()[2])
        mode = data.split()[3]
        if event.interaction.user.id != game_user_id: #not his game
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', description = f'you can\'t stop this game', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return

        if not event.interaction.user.id in hol_games: #not playing
            if mode == 'same':
                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title ='your\'e not playing', color = (255, 0 , 0)),components=[create_help_component(bot)],flags=hikari.MessageFlag.EPHEMERAL)
            else:
                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = hikari.Embed(title ='your\'e not playing', color = (255, 0 , 0)),components = [], flags=hikari.MessageFlag.EPHEMERAL)

            return
        
        if str(game_id) != str(hol_games[game_user_id]['game id']):
            if mode == 'same':
                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title='old Higher or Lower game', color = (255, 0, 0)), components=[create_help_component(bot)])
            else:
                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title='old stop button',description='you can press again to stop the new game', color = (255, 0, 0)), components=[HoL_create_component(bot, game_user_id, game_id=hol_games[game_user_id]['game id'], only_stop=True)])
            return
        

        if hol_games[event.interaction.user.id]['is loading']: #loading game
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,embed = hikari.Embed(title = 'cannot stop a loading game', description = 'please wait until the game stops loading and then stop it', color = (255, 0, 0)), flags=hikari.MessageFlag.EPHEMERAL)
            return

        old_embed = hol_games[event.interaction.user.id]['message embed']
        new_embed = hikari.Embed(title = old_embed.title.replace('?', '') + f'\t game ended\n your score is {hol_games[event.interaction.user.id]["score"]}!', description = old_embed.description.replace('???', f"{hol_games[event.interaction.user.id]['data']['values'][1]:,}"), color = (255, 120, 0)).set_image(old_embed.image)
        new_embed.set_footer(f'score: {hol_games[event.interaction.user.id]["score"]}     stopped game        play again using /play!')
        row = HoL_create_component(bot, event.interaction.user.id, True)

        if data.split()[3] == 'same':
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,embeds = [new_embed], components = [row, create_help_component(bot)], content = f'**play again using ** </play:{bot._slash_commands["play"].instances[None].id}>')
        else:
            try:
                await hol_games[game_user_id]['message'].edit(embeds = [new_embed], components = [row], content = f'**play again using ** </play:{bot._slash_commands["play"].instances[None].id}')
            except hikari.errors.NotFoundError: pass
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(title='stopped', color = (255, 255, 0)), components=[create_help_component(bot)])
        del hol_games[event.interaction.user.id]

        return

    #####################
    if len(data.split(' ')) != 3: #error
        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='invalid button', description = f'the button is invalid, if you think it is a bug please create a ticket in the main server', color = (255, 0 , 0)), component = create_help_component(bot), flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    try:
        game_user_id = int(data.split(' ')[1])
        mode = data.split(' ')[0]
        game_id = int(data.split(' ')[2])
        
        if not event.interaction.user.id in hol_games: #not playing
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='your\'e not playing', description = f'this is not your game! start your *own* game using </play:{bot._slash_commands["play"].instances[None].id}>!', color = (255, 0 , 0)),flags=hikari.MessageFlag.EPHEMERAL)
            return

        elif event.interaction.user.id != game_user_id: #not his game
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='not your game', color = (255, 0 , 0)),components = HoL_create_component(bot, event.interaction.user.id, game_id=hol_games[event.interaction.user.id]['game id'], only_stop=True),flags=hikari.MessageFlag.EPHEMERAL)
            return

        if hol_games[game_user_id]['is loading']: #game is loading
            await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, embed = hikari.Embed(title ='please wait', description = f'please wait until your game is updated', color = (255, 0 , 0)).set_footer('chill out'), flags=hikari.MessageFlag.EPHEMERAL)
            return
        ####################

        hol_games[game_user_id]['is loading'] = True
        hol_games[game_user_id]['last response'] = time.time()
        if (mode == 'h' and hol_games[game_user_id]['data']['values'][0] >= hol_games[game_user_id]['data']['values'][1]) or (mode == 'l' and hol_games[game_user_id]['data']['values'][0] <= hol_games[game_user_id]['data']['values'][1]):
            added = True
            hol_games[game_user_id]['score'] += 1
            old_embed = hol_games[game_user_id]['message embed']
            new_embed = hikari.Embed(title = old_embed.title, description = old_embed.description.replace('???', f"{hol_games[game_user_id]['data']['values'][1]:,}"), color = (0, 255, 0)).set_image(old_embed.image)
            new_embed.set_footer(f'score: {hol_games[game_user_id]["score"]}    LOADING...')
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = new_embed, content = f'**we added alot more games!\ncheck them out in** </help:{bot._slash_commands["help"].instances[None].id}>!\n' + '✅ **correct!** ✅', component = HoL_create_component(bot, game_user_id, True, report_disabled = True, selected_button = mode, game_id = game_id))
            images_data = await asyncio.get_running_loop().run_in_executor(bot.executor, lambda: get_images(words, hol_games[game_user_id]['data']['words'][1], img1 = hol_games[game_user_id]['data']['images'][1]))
            embed_to_send = hikari.Embed(title = 'higher or lower?', description =  f':arrow_up:**`{images_data["words"][0]}`**:arrow_up: - ***{images_data["values"][0]:,}* searches**  - (`higher`)\n\n :arrow_down:**`{images_data["words"][1]}`**:arrow_down: - ***???* searches** - (`lower`)', color = (0, 0, 0))
            #save image
            buf = BytesIO()
            if not game_user_id in hol_games:
                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, content = f'game stopped\n</play:{bot._slash_commands["play"].instances[None].id}>', component = HoL_create_component(bot, 0, True, game_id=0))
                return
            images_data['big image'].save(buf, format = 'PNG')
            embed_to_send.set_footer(f'score: {hol_games[game_user_id]["score"]}')
            row = HoL_create_component(bot, game_user_id, game_id = game_id)
            message = hol_games[game_user_id]['message'] 
            message = await bot.rest.edit_message(event.interaction.channel_id, event.interaction.message.id,content = f'**we added alot more games!\ncheck them out in** </help:{bot._slash_commands["help"].instances[None].id}>!', attachments=[hikari.files.Bytes(buf.getvalue(), f'which-one-is-higher {random.randint(1, 100000)}.png')], embed = embed_to_send, component = row)
            score = hol_games[game_user_id]['score']
            hol_games[game_user_id]['is loading'] = False
            del hol_games[game_user_id]
            hol_games[game_user_id] = {'score' : score, 'data' : images_data, 'game id': game_id, 'message' : message, 'message embed': embed_to_send, 'is loading': False, 'last response': time.time()}
        
        else: #lost
            old_embed = hol_games[game_user_id]['message embed']
            new_embed = hikari.Embed(title = old_embed.title.replace('?', '') + f'\t game ended\n your score is {hol_games[game_user_id]["score"]}!', description = old_embed.description.replace('???', f"{hol_games[game_user_id]['data']['values'][1]:,}"), color = (255, 0, 0)).set_image(old_embed.image)
            new_embed.set_footer(f'score: {hol_games[game_user_id]["score"]}     GG        play again using /play!')
            row = HoL_create_component(bot, game_user_id, True)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed = new_embed, content = f'❌ **better luck next time** ❌\n</play:{bot._slash_commands["play"].instances[None].id}>', components = [row, create_help_component(bot)])
            hol_games[game_user_id]['is loading'] = False
            del hol_games[game_user_id]
    except hikari.errors.NotFoundError:
        if event.interaction.user.id in hol_games and event.interaction.user.id == game_user_id:
            hol_games[event.interaction.user.id]['is loading'] = False
            if added: hol_games[game_user_id]['score'] -= 1
            try:
                await bot.rest.edit_message(event.interaction.channel_id, event.interaction.message.id, embed = hol_games[event.interaction.user.id]['message embed'].set_footer(f'score: {hol_games[event.interaction.user.id]["score"]}    LAG, please click again'))
            except:
                if hol_games[game_user_id]['is loading']:
                    await send_DM(bot, int(event.interaction.user.id), embed = hikari.Embed(title = 'it looks like your\'e *Higher or Lower* game was deleted while loading', description='for unknown reason, the game cannot start\n\ntry playing here in the DM where there are no interruptions', color = (255, 0,0)))