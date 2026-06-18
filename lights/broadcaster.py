import socket, struct, time, threading
from config import *

broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

broadcast_socket.bind(("", MULTICAST_PORT))

mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
broadcast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
heartbeat_socket.bind(("", HEARTBEAT_PORT))
heartbeat_socket.setblocking(False)

clients: list[str] = []


def listen_for_clients():
    global clients
    while True:
        data, addr = broadcast_socket.recvfrom(1024)
        if data == b"Searching for sender":
            if addr[0] not in clients:
                clients.append(addr[0])

def listen_for_heartbeats():
    global clients
    last_seen = {}
    while True:
        time.sleep(0.0001)
        checked_clients = clients.copy()
        for client in checked_clients:
            if not client in last_seen: #new client
                last_seen[client] = time.time()
            if time.time() - last_seen[client] > 1: #client is dead
                clients.remove(client)
                del last_seen[client]
        try:
            while True: #read all awaiting heartbeats
                data, addr = heartbeat_socket.recvfrom(1024)
                last_seen[addr[0]] = time.time()
        except BlockingIOError:
            continue


def init():
    threading.Thread(target=listen_for_clients, daemon=True).start()
    threading.Thread(target=listen_for_heartbeats, daemon=True).start()

def send_message(message:bytes):
    broadcast_socket.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))

def send_frame(rgb_list:list[list[int, int, int]]):
    global clients
    """Send one frame and wait for the 'RDY' response for flow control."""
    
    if len(clients) == 0:
        return
    
    payload = bytearray(N_PIXELS * 3)
    idx = 0
    for r, g, b in rgb_list:
        payload[idx] = r & 0xFF
        payload[idx + 1] = g & 0xFF
        payload[idx + 2] = b & 0xFF
        idx += 3

    for client in clients:
        data_socket.sendto(payload, (client, DATA_PORT))

