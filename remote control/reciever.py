import json
import os
import socket
import time
from threading import Thread
import readchar
import sys


def clear_console():
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


def spacial_event(command, response, timeout=60):
    '''sends terminal command. if response is True. it will catch response'''
    global client_socket, active_heartbeat, global_response
    active_heartbeat = False
    try:
        client_socket.send(json.dumps({'run': [response, command]}).encode())
        if not response:
            active_heartbeat =True
            return

        while global_response == None: pass

        response = global_response.decode()
        active_heartbeat =True
        return response
    except socket.timeout:
        active_heartbeat =True
        return colors.color((255, 0,0)) + 'didn\'t respond in '+timeout+' seconds' + colors.reset
    except Exception as e:
        active_heartbeat =True
        return colors.color((255, 0,0)) + 'unkown error: '+ str(e) + colors.reset



def send_mouse_once(direction = None, button = None):
    if direction is not None:
        if direction == 'up left':
            client_socket.send(json.dumps({'move mouse relative': [-20, -20]}).encode())
        elif direction == 'up':
            client_socket.send(json.dumps({'move mouse relative': [0, -30]}).encode())
        elif direction == 'up right':
            client_socket.send(json.dumps({'move mouse relative': [20, -20]}).encode())
        elif direction == 'down left':
            client_socket.send(json.dumps({'move mouse relative': [-20, 20]}).encode())
        elif direction == 'down':
            client_socket.send(json.dumps({'move mouse relative': [0, 30]}).encode())
        elif direction == 'down right':
            client_socket.send(json.dumps({'move mouse relative': [20, 20]}).encode())
        elif direction == 'left':
            client_socket.send(json.dumps({'move mouse relative': [-30, 0]}).encode())
        elif direction == 'right':
            client_socket.send(json.dumps({'move mouse relative': [30, 0]}).encode())
        
        elif direction == 'scroll up':
            client_socket.send(json.dumps({'scroll': 0.5}).encode())
        elif direction == 'scroll down':
            client_socket.send(json.dumps({'scroll': -0.5}).encode())
    if button != None:
        client_socket.send(json.dumps({'click': button}).encode())

def send_keyboard_once(key, mode = 'type'):
    global client_socket
    if key == '': return
    client_socket.send(json.dumps({mode: key}).encode())


class colors():
    reset = '\033[0m'
    under = '\033[32;4m'
    def color(rgb, colored = 'text'):
        rgb = [str(x) for x in rgb]
        if colored == 'text':
            return f'\033[38;2;{";".join(rgb)}m'
        else:
            return f'\033[48;2;{";".join(rgb)}m'
    

active_heartbeat = True #set to False if the heartbeat needs to pause
def heartbeat(client_socket):
    global active_heartbeat, global_response
    global_response = None #to other threads that needs response
    while True:
        try:
            client_socket.send(b'heartbeat')
        except Exception as e:
            print('failed to send heartbeat', e)
            client_socket.close()
            os._exit(1)
        try:
            response = client_socket.recv(1024)
            global_response = None
            if response == b'heartbeat':
                pass
            elif response == b'exit':
                print('requested exit')
                client_socket.close()
                os._exit(1)
            else:
                global_response = response
        except TimeoutError:
            print('timeout error in heartbeat')
            client_socket.send(b'exit')
            time.sleep(1)
            client_socket.close()
            os._exit(1)
        except Exception as e:
            print('failed to recieve heartbeat', e)
        time.sleep(3)
        #while not active_heartbeat: #pause
        #    pass



convert_table = {"\\x1a": "\x1a","\\x18": "\x18","\\x03": "\x03","\\x16": "\x16","\\x02": "\x02","\\x0e": "\x0e","\\r": "\n","\\x01": "\x01","\\x13": "\x13","\\x04": "\x04","\\x06": "\x06","\\x07": "\x07","\\x08": "\x08","\\n": "\n","\\x0b": "\x0b","\\x0c": "\x0c","\\x1f": "\x1f","\\x11": "\x11","\\x17": "\x17","\\x05": "\x05","\\x12": "\x12","\\x14": "\x14","\\x19": "\x19","\\x15": "\x15","\\t": "\t","\\x0f": "\x0f","\\x10": "\x10","\\x1b": "\x1b","\\x1d": "\x1d","\\x86": "\x86","\\x1c": "\x1c", "\\x7f": "\x7f"} #\r = \n beacause enter sends \r even though its \n
class ui():
    '''here the ui takes place  the run command is a loop function, there is a function for each option (keyboard pressed)'''
    def __init__(self):
        self.command_prompt = ''
        self.command_result = ''
        self.mode = 'normal' #normal command text combo (combination of keys)
        self.extra_text = ''

    def print_screen(self):
        terminal_size = os.get_terminal_size()
        clear_console()
        print(f'{colors.color([0,255,0], "")}connected to 127.0.0.1{colors.reset}')
        print(f'command: {self.command_prompt}')
        print('\n\n')
        print((colors.color([0,0,255], '') + ' ' * terminal_size.columns) + colors.reset)
        print(self.command_result)
        print((colors.color([0,0,255], '') + ' ' * terminal_size.columns) + colors.reset)
        print('move with tyu,gj,vbn\nlift click F\nrigth click K\nmiddle click H\nscroll with SX')
        print(f'{colors.color([255,255,0])}mode is {self.mode}' + colors.reset)
        if self.mode != 'normal':
            print(f'{colors.color([0,0,255])}press esc to exit {self.mode} mode' + colors.reset)
        else:
            print(f'{colors.color([0,0,255])}press w for typing mode' + colors.reset)
            print(f'{colors.color([0,0,255])}press c for command mode' + colors.reset)
            print(f'{colors.color([0,0,255])}press o to send combination of keys' + colors.reset)

        print(self.extra_text)
        self.extra_text = ''

    def run(self):
        key = None
        while True:
            self.print_screen()
            if key != None:
                print(f'pressed key: {key}')

            key = repr(readchar.readkey())[1:-1]
            if key in list(convert_table.keys()):
                key = convert_table[key]


            if self.mode in 'text' and (key == '\x1b' or key == '\\'): #exit
                self.mode = 'normal'
            
            if self.mode == 'normal': #mode changer
                if key.lower() == 'w':
                    self.mode = 'text'
                if key.lower() == 'c':
                    self.mode = 'command'
                    command_confirm = False
                    self.command_prompt = ''
                    self.command_result = ''
                    time.sleep(0.5)
                if key.lower() == 'o':
                    self.mode = 'combo'
                    combo = []
                    combo_confirm = False
                    time.sleep(0.5)
            
            if self.mode == 'normal':
                if key in 'TYUGHJVBNSXFK'.lower(): #mouse
                    key = key.lower()
                    if key in 'TYUGJNBV'.lower(): #move
                        if key == 't':
                            send_mouse_once('up left')
                        elif key == 'y':
                            send_mouse_once('up')
                        elif key == 'u':
                            send_mouse_once('up right')
                        elif key == 'g':
                            send_mouse_once('left')
                        elif key == 'j':
                            send_mouse_once('right')
                        elif key == 'v':
                            send_mouse_once('down left')
                        elif key == 'b':
                            send_mouse_once('down')
                        elif key == 'n':
                            send_mouse_once('down right')
                    elif key in 'FHK'.lower(): #click
                        if key == 'f':
                            send_mouse_once(button = 'left')
                        elif key == 'h':
                            send_mouse_once(button = 'middle')
                        elif key == 'k':
                            send_mouse_once(button='right')
                    else: #scroll
                        if key == 's':
                            send_mouse_once(direction = 'scroll up')
                        else:
                            send_mouse_once(direction ='scroll down')

            if self.mode == 'text': #text mode
                send_keyboard_once(key)
            
            if self.mode == 'combo':
                self.extra_text += 'combo mode is active, press keys to add them to the combo and press esc to confirm/cancel\n'
                if combo_confirm == False:
                    if (key == '\x1b' or key == '\\'):
                        combo_confirm = True
                        self.extra_text += 'send? (Y/n)\n'

                    else:
                        if key in combo:
                            self.extra_text += key + ' is already in the combo\n'
                        else:
                            combo.append(key)
                else:
                    if key.lower() == 'y':
                        send_keyboard_once(combo, 'press')
                        self.mode = 'normal'
                        self.extra_text += 'sent ' + ' + '.join(combo)
                        time.sleep(1)
                    elif key.lower() == 'n':
                        self.mode = 'normal'
                        self.extra_text += 'canceled\n'
                        time.sleep(1)
                    else:
                        self.extra_text += 'press (Y/n)\n'
                self.extra_text += 'current combo: '+ ' + '.join(combo) + '\n'

            if self.mode == 'command':
                self.command_prompt = self.command_prompt.replace('\x08', '').replace('\x7f', '')
                if not command_confirm:
                    if key != '\n':
                        if (key == '\x08' or key == '\x7f') and self.command_prompt != '':
                            self.command_prompt = self.command_prompt[:-1]
                            time.sleep(0.5)
                        self.command_prompt += key
                    else: 
                        self.extra_text += 'do you want to get response from the command? press esc to cancel(Y/n)\n' 
                        command_confirm = True   
                else:
                    if key.lower() == 'y':
                        #send command with
                        self.mode = 'normal'
                        print('sent command, waiting for response') #FIX LINUX BACKSAPCE AND ESCAPE BUG
                        self.command_result = spacial_event(self.command_prompt, True)
                        time.sleep(1)
                    elif key.lower() == 'n':
                        self.mode = 'normal'
                        self.extra_text += 'sent command\n'
                        spacial_event(self.command_prompt, False)
                        time.sleep(1)
                    elif key.lower() == (key == '\x1b' or key == '\\'):
                        self.mode = 'normal'
                        self.extra_text +='canceled\n'
                        time.sleep(1)
                    else:
                        self.extra_text += 'press (Y/n) or esc\n'


            if key == 'q' and self.mode == 'normal': #exit
                print(' closed')
                client_socket.send(b'exit')
                time.sleep(1)
                client_socket.close()
                os._exit(1)



#create TCP scoket and connect to server in 0.0.0.0:29767
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.bind(('0.0.0.0', 29767))
client_socket.listen(1)



running = False



print('connecting...', end = '\r')

while True:
    try:
        (client_socket, _) = client_socket.accept()
        running = True
        break
    except:
        pass
    time.sleep(0.2)
print('connected         ')
client_socket.settimeout(10)
Thread(target=lambda: heartbeat(client_socket)).start()
screen = ui()
Thread(target = screen.run).start()
