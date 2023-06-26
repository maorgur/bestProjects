import json
from os import listdir
import os.path
import socket
import sys
from time import sleep
from subprocess import run
from threading import Thread
import time
import mouse
import keyboard

hostIP = '127.0.0.1' #host ip, 127.0.0.1 means this machine

def filter_keys(keys):
    if 'eight' in keys and 'up' in keys:
        del keys[keys.index('eight')]
    if 'two' in keys and 'down' in keys:
        del keys[keys.index('two')]
    if 'four' in keys and 'left' in keys:
        del keys[keys.index('four')]
    if 'six' in keys and 'right' in keys:
        del keys[keys.index('six')]
    if 'h' and 'backspace' in keys:
        del keys[keys.index('h')]
    return keys

def run_socket(client_socket):
    global last_response
    try:
        '''all the to handle the client's request'''
        #recive messages loop
        client_socket.settimeout(10)
        while True:
            sleep(0.1)
            response = str(client_socket.recv(1024).decode())

            if response == '':
                response = r'{}'
            else: last_response = time.time() #when the other side disconnects unexpectedly, it causes infinite '' response

            #heartbeat
            if response == 'heartbeat':
                print('    heartbeat received',time.time(), end = '\r')
                client_socket.send(b'heartbeat')
                response = r'{}'
            response = json.loads(response[:response.find('}') + 1])
            print(response, end = '\r')
            for key in response.keys():
                if key == 'move mouse':
                    mouse.move(response[key][0], response[key][1])
                elif key == 'move mouse relative':
                    mouse.move(response[key][0], response[key][1], False)
                elif key == 'click':
                    mouse.click(button = response[key])
                elif key == 'type':
                    if sys.platform == 'win32':
                        response[key] = response[key].replace('\x7f', '\x08')
                    else:
                        response[key] = response[key].replace('\x08', '\x7f')
                    keyboard.write(response[key])
                elif key == 'press':
                    if sys.platform == 'win32':
                        response[key] = response[key].replace('\x7f', '\x08')
                    else:
                        response[key] = response[key].replace('\x08', '\x7f')
                    keyboard.send(' + '.join(response[key]).replace('control', 'ctrl'))
                elif key == 'scroll':
                    mouse.wheel(response[key])
                elif key == 'run':
                    return_response = response[key][0]
                    command = response[key][1]
                    if sys.platform == 'win32' and return_response and command.startswith('dir '):
                        try:
                            dir = command[4:]
                        except IndexError:
                            runc = 'specify value after dir'
                        else:
                            if not os.path.exists(dir) and not os.path.isdir(dir):
                                runc = 'file does not exist'
                            elif os.path.isdir(dir):
                                runc = f'files in {dir}: \n' + '\t'.join(listdir(dir))
                            elif os.path.getsize(dir) > 4000000:
                                runc = f'file size is {os.path.getsize(dir):,} > {4000000:,}'
                            else:
                                try:
                                    with open(dir, 'r') as f:
                                        data = f.read()
                                        runc = f'content of {dir}:\n\n' + data
                                except Exception as e:
                                    runc = f'failed to open file: {e}\n\nopening files that are not text can lead to errors'


                        client_socket.send(runc.encode())

                    else:
                        try:
                            if return_response:
                                Thread(target = lambda: client_socket.send(run(command, capture_output = True).stdout.decode().encode())).start()
                            else:
                                Thread(target = lambda: os.system(command)).start()
                        except FileNotFoundError:
                            client_socket.send(b'error: no such command')
                        except Exception as e:
                            print(e)
                            client_socket.send(b'got an error while trying to run remote command:\n' + str(e).encode())

                elif key == 'exit':
                    print('closing connection')
                    client_socket.close()
                    break
                else:
                    client_socket.send(json.dumps(['error', 'unknown command']).encode())
    except TimeoutError:
        client_socket.send(b'exit')
        print('closing connection due to timeout')
        time.sleep(1)
        client_socket.close()
        os._exit(1)
    except Exception as e:
        print(e, '5')
        print(response)
        server_socket.close()
        os._exit(1)


def timeout_loop():
    '''closes code when timeout happens
    normal sock.settimeout doesn't work '''
    global last_response, client_socket

    while True:
        time.sleep(1)
        if time.time() - last_response > 10:
            client_socket.send(b'exit')
            time.sleep(1)
            print('closing connection due to timeout')
            os._exit(1)


last_response = time.time()

while True:
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connected = False
    running = True
    while True:
        try:
            client_socket = server_socket
            client_socket.connect((hostIP, 29767))
            print(f'connected to client')

            connected = True
            Thread(target=timeout_loop).start()
            run_socket(client_socket)
        except OSError as e:
            print(e, 'WHILE TRYING TO CONNECT FROM START')
            time.sleep(2)
