
from datetime import datetime as dt
import requests
from threading import Thread

def etcTprint(*args, end = None, timestamp = False, program = True, webhook = True, color = None):
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
        tprint += 'DISCORD HoL'
    
    if tprint == None: #for weird cases
        print(*args, end = end)
        return
    print(f'[{tprint}]:' + ''.join([f"\033[38;2;{color[0]};{color[1]};{color[2]}m" for _ in range(1) if color != None]), *args,'\033[0m', end = end)
    if webhook:
        payload_content = ' '.join([str(arg).replace('\n', '''
        ''').replace('\t', '    ') for arg in list(args)])
        Thread(target = lambda: requests.post('https://discord.com/api/webhooks/1083505380245655643/Jp5j-gPqrPUyeCJJZ8_hSACf34cspYg-IqZaP-impCW258KDZxSXtqxRndrQzpV1rby0', data = {"content": payload_content,"embeds": None,"username": "Higher or Lower","attachments": [], "avatar_url": "https://cdn.discordapp.com/app-icons/999648623170162779/f03519d9cfc2d7a06060150ca6cf4443.png?size=256"})).start()


etcTprint('starting etc...            ', end = '\r', webhook=False)
import hikari



def create_game_suggestion(value, bot=None):
    '''creats text prompt to guess the word using id
    
    returns title, description, and component'''

    row = bot.rest.build_modal_action_row()
    if len(value) == 5:
        value.append(950)
    row.add_text_input(value[0], value[1], placeholder = value[2], required = value[3], style = value[4], max_length = value[5])
    return row

def create_help_component(bot):
    '''creats row of add to server, main server, website links'''
    row = bot.rest.build_message_action_row()
    row.add_link_button("https://discord.com/api/oauth2/authorize?client_id=1027590480139137175&permissions=0&scope=bot%20applications.commands", label = "add", emoji = '➕')
    row.add_link_button("https://discord.gg/P5dYvqcexf", label ="main server", emoji = '📨')
    row.add_link_button("https://maorgur500.wixsite.com/drife-bots/", label = "website", emoji = '🌐')
    return row

async def suggest_command(ctx, bot):
    await ctx.event.interaction.create_modal_response(title = "game suggestion!", components = [create_game_suggestion(x, bot=bot) for x in [["name","what is the name of the game?", "you can make up a name", True, hikari.TextInputStyle.SHORT], ["target", "what is the \"target\" in this game?","like: getting the sequence right", True, hikari.TextInputStyle.SHORT], ["rules", "explain the game","preffered as steps", True, hikari.TextInputStyle.PARAGRAPH], ["example", "example","not required", False, hikari.TextInputStyle.PARAGRAPH], ["none", "thanks for helping!","join the support server so i reach out to you", False, hikari.TextInputStyle.SHORT]]], custom_id = "support game")


async def send(bot, channel_id, content = None, embed = None, reply = None, attachment = None): #send in guild
    '''sendes message using REST API'''
    if attachment == None:
         await bot.rest.create_message(channel_id, content, embed = embed, reply = reply)
    else:
        await bot.rest.create_message(channel_id, content, embed = embed, reply = reply, attachment = attachment)

async def suggest_update(event: hikari.InteractionCreateEvent, bot):
    if not isinstance(event.interaction, hikari.ModalInteraction):
        return
    if not event.interaction.custom_id.startswith('support game'): return
    suggestion = {event.interaction.components[field].components[0].custom_id: event.interaction.components[field].components[0].value for field in range(4)}
    etcTprint(f"got a game suggestion from {event.interaction.member.id}:\n", "\n\n".join([f"{key}: {value}" for key, value in list(suggestion.items())]), color= (0, 255, 0))
    embed = hikari.Embed(
    description="user id: " + str(event.interaction.member.id),
    color = (0, 255, 0)

    ).set_author(name = event.interaction.member.username + ' @'+str(event.interaction.member.global_name), url = 'https://my-cool-app.com', icon = event.interaction.member.avatar_url.url)
    for key, value in suggestion.items():
        embed.add_field("__" + key + "__", value + ".")

    await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, content = "thanks for suggesting a game!\ngo to the main server so i can contact you\n\nyour suggestion: ", embed=embed, flags=hikari.MessageFlag.EPHEMERAL, component=create_help_component(bot))
    await send(bot, 1019552770178695188, content = f'**someone suggested a game!**',embed = embed) 
    
    
