# this is the main file of the bot Higher or Lower in discord.com
#link to the original bot: https://discord.com/application-directory/999648623170162779
#DO NOT COPY THIS BOT


from datetime import datetime as dt  # used in tprint
import sys, requests
from threading import Thread

sys.dont_write_bytecode = True
from HoL import *
from scramble import *
from simon import *
from matching import *
from jokes import *
from etc import *
from nasa import *
from apis import *


def tprint(*args, end=None, timestamp=False, program=True, webhook=True, color=None):
    '''tprints with file name and timestamp'''
    tprint = ''
    if timestamp:
        tprint += '.'.join([str(x) for x in dt.now().timetuple()[:3]])  # date
        tprint += ' '
        tprint += ':'.join([str(x) for x in dt.now().timetuple()[4:7]])  # time
        tprint = tprint[2:]  # remove the first digits of the year

    if timestamp and program:
        tprint += '  '  # space between sections

    if program:  # diffrent between programs
        tprint += 'DISCORD HoL'

    if tprint == None:  # for weird cases
        print(*args, end=end)
        return
    print(f'[{tprint}]:' + ''.join([f"\033[38;2;{color[0]};{color[1]};{color[2]}m" for _ in range(1) if color != None]),
          *args, '\033[0m', end=end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target=lambda: requests.post(
            'https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0',
            data={"content": payload_content, "embeds": None, "username": "Higher or Lower", "attachments": [],
                  "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()


tprint('starting bot...                ', end='\n')
import asyncio, json, os, random, time
import hikari, lightbulb, requests
from PIL import Image

start_time = time.time()
general_help = ''

# components
def create_help_component():
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/application-directory/999648623170162779", label="view bot", emoji='👁️')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label="main server", emoji='📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label="website", emoji='🌐')
    return row


def create_help_dropdown_components(user_id, active=[]):
    row = bot.rest.build_message_action_row()

    dropdown = row.add_text_menu(f'help menu {user_id}', placeholder=f'there are {len(bot._slash_commands) - 4} commands', max_values=1)
    dropdown.add_option('Higher or Lower', 'HoL', description='how to play the Higher or Lower Game!', emoji='↕️',is_default='HoL' in active)
    dropdown.add_option('joke', 'joke', description='make your\'e day better with a joke!', emoji='🤣',is_default='joke' in active)
    dropdown.add_option('Simon', 'simon', description='how to play color simon!', emoji='🔴',is_default='simon' in active)
    dropdown.add_option('word scramble', 'scramble', description='how to play word scramble!', emoji='🔤',is_default='scramble' in active)
    dropdown.add_option('matching', 'matching', description='how to play color matching!', emoji='🎨',is_default='matching' in active)
    dropdown.add_option('chess puzzle', 'chess', description='find the correct moves to solve the puzzle', emoji='♟️',is_default='chess' in active)
    dropdown.add_option('Astronomy Picture', 'astronomy-picture', description='Astronomy Picture of the Day by NASA',emoji='🛰️', is_default='astronomy-picture' in active)
    dropdown.add_option('bored', 'bored', description='find an activity to do',emoji='💬', is_default='bored' in active)
    dropdown.add_option('advice', 'advice', description='get a smart advice',emoji='🧠', is_default='advice' in active)
    dropdown.add_option('Tronald dumb', 'tronald', description='find dumb quotes that Donald Trump once said',emoji='🐦', is_default='tronald' in active)
    dropdown.add_option('Chuck Norris', 'chuck-norris', description='get a sentence from the one and only Chuck Norris',emoji='🤠', is_default='chuck-norris' in active)
    return row


# send messages through API
async def send(channel_id, content=None, embed=None, reply=None, attachment=None):  # send in guild
    '''sendes message using REST API'''
    if attachment == None:
        await bot.rest.create_message(channel_id, content, embed=embed, reply=reply)
    else:
        await bot.rest.create_message(channel_id, content, embed=embed, reply=reply, attachment=attachment)


async def send_DM(user, embed=None, content=None, component=None):
    try:
        await (await bot.rest.create_dm_channel(int(user))).send(embed=embed, content=content, component=component)
        return True
    except Exception as e:
        return False


# load jokes.json
with open(f'{directory}/jokes.json', 'r', encoding='UTF-8') as f:
    _jokes_command_list = json.load(f)
# load help.json
with open(f'{directory}/help.json', 'r', encoding='UTF-8') as f:
    help_texts = json.load(f)

bot = lightbulb.BotApp(token='DISCORD-BOT-TOKEN',
                       owner_ids=[595989293961314304, 764883085484883999], )


@bot.command
@lightbulb.command('help', 'get help using the bot!')
@lightbulb.implements(lightbulb.SlashCommand)
async def help_command(ctx: lightbulb.context):
    global general_help
    general_help = f"""**start playing with** </play:{bot._slash_commands['play'].instances[None].id}>, </scramble:{bot._slash_commands['scramble'].instances[None].id}>, </simon:{bot._slash_commands['simon'].instances[None].id}>, </matching:{bot._slash_commands['matching'].instances[None].id}>, </joke:{bot._slash_commands['joke'].instances[None].id}>!
1. **</help:{bot._slash_commands['help'].instances[None].id}>** - shows this message
2. **</ping:{bot._slash_commands['ping'].instances[None].id}>** - get bot latency!
3. **</info:{bot._slash_commands['info'].instances[None].id}>** - get information about Higher or Lower bot!
4. **</suggest:{bot._slash_commands['suggest'].instances[None].id}>** - suggest a new game!"""
    embed = hikari.Embed(title='Help', color=(255, 255, 255))
    embed.add_field(':robot: commands :robot:', general_help, inline=True),
    embed.add_field(':scroll: how to play :scroll:', f'''
**get help about a certain game(s) down below**⬇️
</play:{bot._slash_commands['play'].instances[None].id}>    </scramble:{bot._slash_commands['scramble'].instances[None].id}>    </simon:{bot._slash_commands['simon'].instances[None].id}>    </matching:{bot._slash_commands['matching'].instances[None].id}>    </joke:{bot._slash_commands['joke'].instances[None].id}>''',
                    inline=True)
    embed.add_field(':telephone: support :telephone:', '''
for support, create a ticket in the [main server](https://discord.gg/P5dYvqcexf)
or send a *direct message* to the bot''')
    try:
        await ctx.respond(embed=embed,
                          components=[create_help_dropdown_components(ctx.author.id), create_help_component()])
    except hikari.errors.NotFoundError:
        pass


@bot.command
@lightbulb.command('ping', 'pinging the bot')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.context):
    # check when the message was sent in unix
    try:
        message_time = int(ctx._event.interaction.created_at.timestamp())
        message_time_n = int((time.time() - message_time) * 1000)
        message_time = time.time()
        download_payload = f'read: `{message_time_n} ms` \n respond: `'
        await ctx.respond(embed=hikari.Embed(title=':yellow_circle: ping :yellow_circle:',
                                             description=f'read: `{message_time_n} ms`\n respond: `loading...`',
                                             color=(255, 255, 0)))
        message_time = int((time.time() - message_time) * 1000)
        await ctx.edit_last_response(embed=hikari.Embed(title=':green_circle: ping :green_circle:',
                                                        description=f'{download_payload} {message_time} ms`',
                                                        color=(0, 255, 0)))
    except hikari.errors.NotFoundError:
        pass


@bot.command
@lightbulb.command('info', 'info about Higher or Lower bot!')
@lightbulb.implements(lightbulb.SlashCommand)
async def info(ctx: lightbulb.context):
    global guilds
    try:
        embed = hikari.Embed(
            title='live info',
            description=f'**{len(guilds)} servers are using Higher or Lower**\n\nbot went online <t:{int(start_time)}:R>\n\nthere is {len(bot._slash_commands) - 4} game commands!\n\nif you want to countribute to **Higher or Lower**, </suggest:{bot._slash_commands["suggest"].instances[None].id}> a game!',
            color=(0, 255, 0)
        )
        embed.set_image('https://cdn.discordapp.com/emojis/1072544436216668232.webp?size=512&quality=lossless')
        await ctx.respond(embed=embed, component=create_help_component())
    except hikari.errors.NotFoundError:
        pass


hol_games = {}  # user.id = {score, last_data = {name, image, number}}
hol_play_settings = {}


@bot.command
@lightbulb.command('play', 'start a game!')
@lightbulb.implements(lightbulb.SlashCommand)
async def HoL_command_exec(ctx: lightbulb.context):
    await HoL_command(ctx, bot)


@bot.listen(hikari.InteractionCreateEvent)  # update game
async def HoL_update_exec(event: hikari.InteractionCreateEvent):
    await HoL_update(event, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def report_help_initial(event: hikari.InteractionCreateEvent):
    global image_urls, hol_games
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    if event.interaction.custom_id.startswith('help'):  # help
        for command in list(help_texts["commands"].keys()):
            if event.interaction.custom_id.split()[1] == command:
                embed = hikari.Embed(title = 'how to use ❓', description='\n- '.join(help_texts["commands"][command]["description"]), color = (255, 255, 255))
                embed.add_field(":telephone: support :telephone:", "".join(help_texts["support"]))

                await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed,flags=hikari.MessageFlag.EPHEMERAL)
        return


    elif event.interaction.custom_id != 'HoL report':
        return
    row = bot.rest.build_modal_action_row()
    row.add_text_input('HoL report modal', 'don\'t report for pixelated images!', required=True,
                       style=hikari.TextInputStyle.PARAGRAPH,
                       placeholder='please describe which of the images/keywords is inappropiate and give a short explanation why',
                       max_length=500)
    await event.interaction.create_modal_response('report', custom_id='HoL report modal', component=row)
    return


@bot.listen(hikari.InteractionCreateEvent)  # report handle
async def HoL_report(event: hikari.InteractionCreateEvent):
    if not isinstance(event.interaction, hikari.ModalInteraction): return
    if not event.interaction.components[0].components[0].custom_id.startswith('HoL'): return
    await event.interaction.create_initial_response(  # repond
        hikari.ResponseType.MESSAGE_CREATE, embed=hikari.Embed(title='sent report',
                                                               description=f'**successfully reported images**\n\nyou will get a response in the DM from this bot!',
                                                               color=(255, 255, 0)).add_field('your report',
                                                                                              f'```{event.interaction.components[0].components[0].value}```'),
        flags=hikari.MessageFlag.EPHEMERAL)

    # update image
    if event.interaction.message.interaction.user.id in hol_games:
        row = HoL_create_component(event.interaction.message.interaction.user.id, False, True,
                                   game_id=hol_games[event.interaction.user.id]['game id'])
    else:
        row = HoL_create_component(event.interaction.message.interaction.user.id, True, True)
    await bot.rest.edit_message(event.interaction.channel_id, event.interaction.message.id,
                                content=f':triangular_flag_on_post: report from <@{event.interaction.user.id}>',
                                attachments=[
                                    'https://uxwing.com/wp-content/themes/uxwing/download/web-app-development/image-not-found-icon.png'],
                                component=row)
    if event.interaction.message.interaction.user.id in hol_games:
        if not hol_games[event.interaction.message.interaction.user.id]['is loading']:
            hol_games[event.interaction.message.interaction.user.id]['data']['images'] = [
                Image.new('RGB', (300, 100), (200, 200, 200)), Image.new('RGB', (300, 100), (200, 200, 200))]

    await send(1018541815084879973, content=f'id: {event.interaction.user.id}', embed=
    hikari.Embed(
        title=f':triangular_flag_on_post: report from {event.interaction.user.mention}  {event.interaction.user.username}#{event.interaction.user.discriminator}'
    ).add_field('original message', event.interaction.message.embeds[0].description, inline=True)
               .add_field('report message', f'```{event.interaction.components[0].components[0].value}```',
                          inline=True).add_field('response format',
                                                 'respond to the bot from DM in the format of:\nuser_id image_link message\n\nexample:\n```1234567654754 https://image.com find friends```'),
               attachment=hikari.files.Bytes(requests.get(event.interaction.message.attachments[0].proxy_url).content,
                                             'spoiler_nsfw image.png', spoiler=True))


# scramble
@bot.command
@lightbulb.command('scramble', 'play word scramble!')
@lightbulb.implements(lightbulb.SlashCommand)
async def scramble_command_exec(ctx: lightbulb.context):
    await scramble_command(ctx, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def scramble_update_exec(event: hikari.InteractionCreateEvent):
    await scramble_update(event, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def scramble_modal_response_exec(event: hikari.InteractionCreateEvent):
    await scramble_modal_response(event, bot)


# suggest
@bot.command
@lightbulb.command('suggest', 'suggest a new game!')
@lightbulb.implements(lightbulb.SlashCommand)
async def suggest_command_exec(ctx: lightbulb.context):
    await suggest_command(ctx, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def suggest_update_exec(event: hikari.InteractionCreateEvent):
    await suggest_update(event, bot)


#####
# simon
@bot.command
@lightbulb.command('simon', 'play simon colors!')
@lightbulb.implements(lightbulb.SlashCommand)
async def simon_command_exec(ctx: lightbulb.context):
    await simon_command(ctx, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def simon_game_update_exec(event: hikari.InteractionCreateEvent):
    await simon_game_update(event, bot)


#####
# matching
@bot.command
@lightbulb.command('matching', 'play color matching!')
@lightbulb.implements(lightbulb.SlashCommand)
async def matching_command_exec(ctx: lightbulb.context):
    await matching_command(ctx, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def matching_game_update_exec(event: hikari.InteractionCreateEvent):
    await matching_game_update(event, bot)


@bot.listen(hikari.InteractionCreateEvent)
async def matching_dropdown_update_exec(event: hikari.InteractionCreateEvent):
    await matching_dropdown_update(event, bot)


###
# joke
@bot.command
@lightbulb.option('type', 'what type of joke you want?', required=True,
                  choices=['long joke', 'random thought / joke', 'reddit joke'])
@lightbulb.command('joke', 'make your\'e day better with a joke!')
@lightbulb.implements(lightbulb.SlashCommand)
async def jokes_command_exec(ctx: lightbulb.context):
    await jokes_command(ctx, bot)


###
# nasa
@bot.command
@lightbulb.option('days-back', 'get an image of a previous day', required=False, min_value=0, max_value=10_000,
                  type=int)
@lightbulb.command('astronomy-picture', 'see the Astronomy Picture of the Day by NASA')
@lightbulb.implements(lightbulb.SlashCommand)
async def apod_command_exec(ctx: lightbulb.context):
    await apod_command(ctx, bot)

###
# apis
@bot.command
@lightbulb.option('type', 'what type of activity you want to do?', choices=["education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork"], required=False)
@lightbulb.command('bored', 'find something to do from boredapi.com')
@lightbulb.implements(lightbulb.SlashCommand)
async def bored_command_exec(ctx: lightbulb.context):
    await bored_command(ctx, bot)

@bot.command
@lightbulb.command('advice', 'get a smart advice for life')
@lightbulb.implements(lightbulb.SlashCommand)
async def advice_command_exec(ctx: lightbulb.context):
    await advice_command(ctx, bot)

@bot.command
@lightbulb.command('tronald', 'dumb quotes from donald trump')
@lightbulb.implements(lightbulb.SlashCommand)
async def tronald_command_exec(ctx: lightbulb.context):
    await tronald_dump_command(ctx, bot)

@bot.command
@lightbulb.command('chess', 'solve a chess.com puzzle')
@lightbulb.implements(lightbulb.SlashCommand)
async def chess_puzzle_exec(ctx: lightbulb.context):
    await chess_puzzle_command(ctx, bot)

@bot.command
@lightbulb.command('chuck-norris', 'sentence that Chuck Norris once said')
@lightbulb.implements(lightbulb.SlashCommand)
async def chuck_command_exec(ctx: lightbulb.context):
    await chuck_norris(ctx, bot)

#############################
async def always_running_func(event=None):
    global hol_play_settings, image_urls, simon_games, scramble_games
    iteration = 0  # for stuff that doesn't run every second
    while bot.is_alive:
        try:
            if iteration % 10 == 0:  # check if midnight
                if (dt.utcnow() - dt.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() < 5:
                    hol_play_settings = {}

            if iteration % 60 == 0:  # save info

                # opens urls.json, looking for external changes and then saves the result with the bot added info
                with open(f'{directory}/urls.json') as f:  # gets new images from file
                    temp_image_urls = json.load(f)
                    image_urls_keys = list(image_urls.keys())
                    for key in list(temp_image_urls.keys()):
                        if not key in image_urls_keys:
                            image_urls[key] = temp_image_urls[key]
                    del image_urls_keys

                with open(f'{directory}/urls.json', 'w') as f:
                    json.dump(image_urls, f, indent=4)

            # check if games timeout
            for game in list(hol_games.copy().keys()):  # HoL
                if hol_games[game]['last response'] < time.time() - 60:
                    old_embed = hol_games[game]['message embed']
                    new_embed = hikari.Embed(title=old_embed.title.replace('?',
                                                                           '') + f'\t game ended\n your score is {hol_games[game]["score"]}!',
                                             description=old_embed.description.replace('❔❔❔',
                                                                                       f"{hol_games[game]['data']['values'][1]:,}"),
                                             color=(255, 120, 0)).set_image(old_embed.image)
                    new_embed.set_footer(f'score: {hol_games[game]["score"]}     timeout       play again using /play!')
                    row = HoL_create_component(game, True)
                    _game = hol_games[game]
                    del hol_games[game]
                    await _game['message'].edit(embeds=[new_embed], components=[row, create_help_component()],
                                                content=f'**play again using ** </play:{bot._slash_commands["play"].instances[None].id}>\n```game was inactive for one minute```')

            # check if games timeout
            for game in list(simon_games.copy().keys()):  # simon
                if simon_games[game]['last response'] < time.time() - 4:
                    _game = simon_games[game]
                    del simon_games[game]
                    await _game['message'].edit(
                        embed=hikari.Embed(title='`you didn\'t respond in time!`', color=(255, 0, 0)),
                        components=[create_help_component()],
                        content=f'**play again using ** </simon:{bot._slash_commands["simon"].instances[None].id}>')

            for game in list(scramble_games.copy().keys()):  # scramble
                if scramble_games[game]['last response'] < time.time() - 120:
                    _game = scramble_games[game]
                    del scramble_games[game]
                    await _game['message'].edit(embed=hikari.Embed(title='`you didn\'t respond in time!`',
                                                                   description=f'the scrambled word `{_game["scramble"]}` was *{_game["word"]}*',
                                                                   color=(255, 0, 0)),
                                                components=[create_help_component()],
                                                content=f'**play again using ** </scramble:{bot._slash_commands["scramble"].instances[None].id}>')
            for game in list(matching_games.copy().keys()):  # scramble
                if matching_games[game]['last response'] < time.time() - 60:
                    _game = matching_games[game]
                    del matching_games[game]
                    await _game['message'].edit(embed=hikari.Embed(title='`you didn\'t respond in time!`',
                                                                   description=f'the sequence was `{" ".join(["🟪🟦🟨🟩🟧🟥"[color] for color in _game["sequence"]])}`',
                                                                   color=(255, 0, 0)),
                                                components=[create_help_component()],
                                                content=f'**play again using ** </matching:{bot._slash_commands["matching"].instances[None].id}>')

            if int(time.time()) % 600 == 0:
                await bot.update_presence(
                    status=hikari.Status.ONLINE,
                    activity=hikari.Activity(
                        name='/joke: ' + random.choice(_jokes_command_list),
                        type=hikari.ActivityType.PLAYING
                    ))

            await asyncio.sleep(1)
            iteration += 1
        except Exception as e:
            tprint('got an error in always running func:\t', str(e).replace('\n', '    '), str(e.with_traceback),
                   type(e), end='\r', timestamp=True);
            await asyncio.sleep(5)


@bot.listen(hikari.StartedEvent)
async def play_start(event):
    asyncio.get_event_loop().create_task(always_running_func())


@bot.listen(hikari.InteractionCreateEvent)
async def help_dropdown(event: hikari.InteractionCreateEvent):
    global general_help
    if not isinstance(event.interaction, hikari.ComponentInteraction): return
    if event.interaction.component_type != hikari.ComponentType.TEXT_SELECT_MENU: return
    if not event.interaction.custom_id.startswith('help menu'): return

    if str(event.interaction.member.id) != event.interaction.custom_id.split()[2]:
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE,
                                                        embed=hikari.Embed(title='not your /help',
                                                                           description=f'**this is not your\'e </help:{bot._slash_commands["help"].instances[None].id}>**\nget help using </help:{bot._slash_commands["help"].instances[None].id}>',
                                                                           color=(255, 0, 0)),
                                                        flags=hikari.MessageFlag.EPHEMERAL)
        return

    embed = hikari.Embed(  # always showing
        title='Help',
        color=(255, 255, 255)
    )
    general_help = f"""**start playing with** </play:{bot._slash_commands['play'].instances[None].id}>, </scramble:{bot._slash_commands['scramble'].instances[None].id}>, </simon:{bot._slash_commands['simon'].instances[None].id}>, </matching:{bot._slash_commands['matching'].instances[None].id}>, </joke:{bot._slash_commands['joke'].instances[None].id}>!,
1. **</help:{bot._slash_commands['help'].instances[None].id}>** - shows this message
2. **</ping:{bot._slash_commands['ping'].instances[None].id}>** - get bot latency!
3. **</info:{bot._slash_commands['info'].instances[None].id}>** - get information about Higher or Lower bot!
4. **</suggest:{bot._slash_commands['suggest'].instances[None].id}>** - suggest a new game!"""
    embed.add_field(':robot: commands :robot:', general_help, inline=True)

    #########
    for command in list(help_texts["commands"].keys()):
        if command in event.interaction.values:
            embed.add_field(help_texts["commands"][command]["title"],
                            f'**start using </{command.replace("HoL", "play")}:{bot._slash_commands[command.replace("HoL", "play")].instances[None].id}>**' + "\n" +
                            '\n- '.join(help_texts["commands"][command]["description"]))

    embed.add_field(':telephone: support :telephone:', '\n'.join(help_texts["support"]), inline=True)

    if event.interaction.values == ():
        embed.add_field(':scroll: how to play :scroll:', f'''
**get help about a certain game(s) down below**⬇️''',inline=True)
    #################

    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE, embed=embed, components=[
        create_help_dropdown_components(event.interaction.member.id, event.interaction.values),
        create_help_component()])


@bot.listen(hikari.StartedEvent)
async def on_start(event):
    global guilds
    # print active guilds
    guilds = await bot.rest.fetch_my_guilds()
    for guild in guilds:
        try:
            tprint(guild.name, guild.id, webhook=False)
        except KeyError:
            pass
    tprint(f'ACTIVE ON {len(guilds)} GUILDS', timestamp=True)


@bot.listen(hikari.GuildJoinEvent, hikari.GuildLeaveEvent)
async def server_update(event):
    global guilds
    if isinstance(event, hikari.GuildLeaveEvent):
        if event.old_guild == None: return
        tprint(f'left {event.old_guild.name} ({event.old_guild.id}) with {event.old_guild.member_count} members',
               timestamp=True, color=(255, 0, 0))
    elif isinstance(event, hikari.GuildJoinEvent):
        if event.guild == None: return
        tprint(f'joined {event.guild.name} ({event.guild.id}) with {event.guild.member_count} members', timestamp=True,
               color=(0, 255, 0))
    else:
        print(event)
    # tprint active guilds
    guilds = await bot.rest.fetch_my_guilds()

    tprint(f'ACTIVE ON {len(guilds)} GUILDS', timestamp=True)


@bot.listen(hikari.StoppedEvent)
async def bot_close(event):
    tprint('shutting down bot')


@bot.listen(hikari.DMMessageCreateEvent)
async def remote(event):
    global guilds
    if event.message.content == None:
        return
    try:
        if event.message.content == 'down' and int(event.author.id) in [595989293961314304,
                                                                        764883085484883999]:  # shutdown
            for user in list(hol_games.keys()):
                try:
                    row = HoL_create_component(user, True)
                    await hol_games[user]['message'].edit(
                        embed=hol_games[user]['message embed'].set_footer('game stopped due to bot restart'),
                        content='bot is restarting', component=row)
                    del hol_games[user]
                except:
                    pass
            await bot.close()
            tprint('Stopped bot remotly', timesamp=True)
            os._exit(1)

        elif event.message.content.startswith('leave') and int(event.author.id) in [595989293961314304,764883085484883999]:  # leave servers and get server list
            guild_id = int(event.message.content.split(' ')[-1])
            if not str(guild_id) in [str(guild.id) for guild in guilds]:
                msg = ''
                for guild in guilds:
                    msg += f'{guild.name}:   {guild.id}\n'
                msg += f'total len: {len(guilds)}\n\n**SERVER NOT FOUND**'
                msg = [msg[y - 1500:y] for y in range(1500, len(msg) + 1500, 1500)]
                for text in msg:
                    await send_DM(event.author.id, content=text)
                return

            guild = [guild for guild in guilds if str(guild.id) == str(guild_id)][0]
            tprint(f'sent request to leave guild  {guild.name}  : {guild_id}', timesamp=True)
            await send_DM(event.author.id, content=f'left the  `{guild.name}`  guild: {guild_id}')
            await bot.rest.leave_guild(guild_id)

        elif event.message.content.startswith('info') and int(event.author.id) in [595989293961314304,
                                                                                   764883085484883999]:  # get channels of server and invites

            guild_id = int(event.message.content.split(' ')[-1])
            if not str(guild_id) in [str(guild.id) for guild in guilds]:
                msg = ''
                for guild in guilds:
                    msg += f'{guild.name}:   {guild.id}\n'
                msg += f'total len: {len(guilds)}\n\n**SERVER NOT FOUND**'
                msg = [msg[y - 1500:y] for y in range(1500, len(msg) + 1500, 1500)]
                for text in msg:
                    await send_DM(event.author.id, content=text)
                return

            guild = [guild for guild in guilds if str(guild.id) == str(guild_id)][0]
            tprint(f'info request on  {guild.name}  : {guild_id}')
            try:
                invites = await bot.rest.fetch_guild_invites(guild_id)
            except:
                invites = []
            channels = await bot.rest.fetch_guild_channels(str(guild_id))
            channels_msg = ''
            for channel in channels:
                channel = f'{channel.name}: {channel.id}\t\t{channel.type}\n'
                channels_msg += channel
            channels_msg += f'\n total channels: {len(channels)}'
            await send_DM(event.author.id,
                          content=f'information about `{guild.name}`  guild: {guild_id}\n\n{invites = }\n\nchannels\n{channels_msg}\n{guild.icon_url}')

        elif event.message.content.startswith('command ') and int(event.author.id) in [595989293961314304,
                                                                                       764883085484883999]:
            Thread(target=lambda: os.system(event.message.content[8:])).start()
            await send_DM(event.author.id, content='running command ' + event.message.content[
                                                                        8:] + '\n\nthe command response will never be shown (code design)')

        elif event.message.content.startswith('edit') and int(event.author.id) in [595989293961314304,
                                                                                   764883085484883999]:  # edit urls
            if len(event.message.content.split()) == 2:
                try:
                    del image_urls[event.message.content.split()[1]]
                    del words[event.message.content.split()[1]]  # temoporary removal of word, for change later
                    await send_DM(event.author.id, content='removed successfully: ' + event.message.content.split()[1])
                except KeyError:
                    await send_DM(event.author.id, content='not found')
            else:
                try:
                    image_urls[event.message.content.split()[1]] = ''.join(event.message.content.split()[2:])
                    await send_DM(event.author.id,
                                  content='changed successfully: `' + event.message.content.split()[1].replace('+',
                                                                                                               ' ') + '` -> ```' + ''.join(
                                      event.message.content.split()[2:]) + '```')
                except (KeyError, IndexError):
                    await send_DM(event.author.id, content='not found')
    except:
        pass


@bot.listen(hikari.DMMessageCreateEvent)
async def forward_dm(event):
    if event.author.id == bot.get_me().id: return
    if event.message.content == None:
        await send_DM(event.author.id, embed=hikari.Embed(title='invalid message',
                                                          description='please send text, only plain text will be sent (links included)',
                                                          color=(255, 0, 0)).set_footer(
            'creating a ticket in the main server is recommended'))
        return
    try:
        if event.author.id in [595989293961314304, 764883085484883999] and True in [event.message.content.startswith(x)
                                                                                    for x in
                                                                                    ['down', 'info', 'leave', 'command',
                                                                                     'edit']]: return  # don't report remote commands
        if not event.author.id in [595989293961314304, 764883085484883999]:
            if not event.author.id == 999648623170162779 and event.embed.title == 'response for your report':
                await send(channel_id=1019552770178695188,
                           content=f'message from {event.author.mention}  {event.author.username}#{event.author.discriminator}\n\n````' + event.message.content + '```')
                return
    except Exception as e:
        tprint('got an error while forwaring DM. message:', event.message.content, '\nerror:', e)

    content = event.message.content
    user = content.split()[0].replace('<', '').replace('>', '').replace('@', '').strip()
    if not user.isdigit():
        return
    image = content.split()[1]

    await send_DM(user, embed=hikari.Embed(title='response for your report',
                                           description='```' + ' '.join(content.split()[2:]) + '```',
                                           color=(255, 255, 255)).set_image(image).add_field('contact back ☎️',
                                                                                             'if you have anything to add, it is recommended to continue in the [main server](https://discord.gg/P5dYvqcexf) by opening a ticket.\n\n you can also send a message here but it\'s not recommended'),
                  component=create_help_component())
    await send(channel_id=1019552770178695188, content=f'sent report to <@' + user + '>',
               embed=hikari.Embed(title='response for your report',
                                  description='```' + ' '.join(content.split(' ')[2:]) + '```',
                                  color=(255, 255, 255)).set_image(image).add_field('contact back ☎️',
                                                                                    'if you have anything to add, it is recommended to continue in the [main server](https://discord.gg/P5dYvqcexf) by opening a ticket.\n\n you can also send a message here but it\'s not recommended'))


bot.run(
    status=hikari.Status.ONLINE,
    activity=hikari.Activity(
        name="bot started",
        type=hikari.ActivityType.PLAYING,
    )
)
