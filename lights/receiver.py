#run this script to use this program as a receiver

import socket
from config import *
import terminal
import tools

import time, threading

if SEND_TO_ARDUINO:
    import raw_serial
    arduino = raw_serial.LEDController()

if SEND_TO_SCREEN:
    import screen
    screen.start_window()

if SEND_TO_PC_LIGHTS:
    import pc_lights
    pc_lights_amount = pc_lights.get_pixels_count()

if SEND_TO_BULBS:
    import light_bulbs
    BULB_COUNT = light_bulbs.get_bulb_count()



MULTICAST_TTL = 2

multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_socket.bind(("0.0.0.0", DATA_PORT))
data_socket.settimeout(1)

heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_ip = None
def get_server_ip():
    global server_ip
    while True:
        if server_ip is None:
            multicast_socket.sendto(b"Searching for sender", (MULTICAST_GROUP, MULTICAST_PORT))
        time.sleep(1)

def heartbeat():
    while True:
        if server_ip is not None:
            heartbeat_socket.sendto(b"HB", (server_ip, HEARTBEAT_PORT))
        time.sleep(0.5)

def decode_frame(response:bytes):
    rgb_list = []
    for i in range(0, len(response), 3):
        r = response[i]
        g = response[i + 1]
        b = response[i + 2]
        rgb_list.append([r, g, b])
    return rgb_list

RECEIVE_BUFFER_SIZE = 2
while RECEIVE_BUFFER_SIZE < N_PIXELS * 3:
    RECEIVE_BUFFER_SIZE *= 2 #buffer has to be in magnitudes of 2 cuz this is what socket wants


frame = BLACK_FRAME
def print_to_terminal_on_loop():
    while True:
        layered_frames = [{"name": "", "modifiers": [], "frame": frame, "mode name": ""}]
        terminal.update_led_strip(frame, layered_frames)

        terminal.print_terminal()

        time.sleep(0.001)


def update_arduino_on_loop():
    while True:
        arduino.send_frame(frame)

        time.sleep(0.001) #unlock the GIL


def update_light_bulbs_on_loop():
    while True:
        colors_to_bulbs = []
        for bulb_color in range(BULB_COUNT):
            start_index = int(bulb_color * N_PIXELS / BULB_COUNT)
            end_index = int((bulb_color + 1) * N_PIXELS / BULB_COUNT)
            average_color = [sum(pixel[i] for pixel in frame[start_index:end_index]) // (end_index - start_index) for i in range(3)]
            colors_to_bulbs.append(average_color)

        light_bulbs.update_bulbs(colors_to_bulbs, True)

        time.sleep(0.001) #unlock the GIL

def update_pc_lights_on_loop():
    while True:
        pc_lights_frame = tools.resize_strip_to_size(frame[HALF_PIXELS:], pc_lights_amount)
        pc_lights.update(pc_lights_frame)

        time.sleep(0.001) #unlock the GIL



threading.Thread(target=print_to_terminal_on_loop, daemon=True).start()

if SEND_TO_ARDUINO:
    threading.Thread(target=update_arduino_on_loop, daemon=True).start()

if SEND_TO_PC_LIGHTS:
    threading.Thread(target=update_pc_lights_on_loop, daemon=True).start()

if SEND_TO_BULBS:
    threading.Thread(target=update_light_bulbs_on_loop, daemon=True).start()

###network
threading.Thread(target=get_server_ip, daemon=True).start()
threading.Thread(target=heartbeat, daemon=True).start()

terminal.init(False)
while True:
    try:
        raw_response, addr = data_socket.recvfrom(RECEIVE_BUFFER_SIZE)
    except socket.timeout:
        server_ip = None
        continue
    else:
        server_ip = addr[0]

    frame = decode_frame(raw_response)

    if SEND_TO_SCREEN:
        screen.set_colors(frame)
