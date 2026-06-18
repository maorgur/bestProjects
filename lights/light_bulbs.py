import yeelight, time
import tools
from config import MAX_BULBS_FPS, BULB_COUNT, BULB_TYPE
import threading
import socket

def discover_bulbs(timeout=5):
    """
    The yeelight lib has problems with interface, so this is my modification of it
    """
    def get_default_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()

    #send broadcast
    discover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    discover_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    discover_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(get_default_local_ip()))
    msg = "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            "HOST: " + "239.255.255.250:1982",
            'MAN: "ssdp:discover"',
            "ST: wifi_bulb",
        ]
    )
    discover_socket.sendto(msg.encode(), ("239.255.255.250", 1982))

    #listen back
    discover_socket.settimeout(timeout)
    bulbs = set()
    while len(bulbs) < BULB_COUNT:
        try:
            data, addr = discover_socket.recvfrom(65507)
        except socket.timeout:
            break
        else:
            bulbs.add(addr)

    return bulbs


print("Discovering bulbs...")

discover_result = discover_bulbs()
while len(discover_result) < BULB_COUNT:
    print("Found only", len(discover_result), "bulb(s), retrying...", ", ".join([bulb[0] for bulb in discover_result]))
    discover_result = discover_bulbs()

print("Found bulbs:", ", ".join([bulb[0] for bulb in discover_result]), "continuing...")

bulbs:list[yeelight.Bulb] = []
for bulb in discover_result:
    bulbs.append(yeelight.Bulb(bulb[0], effect='smooth', duration=1000, model = BULB_TYPE))


for bulb in bulbs:
    bulb.turn_on()
    try:
        bulb.get_properties()
        if not bulb.music_mode:
            bulb.start_music()
    except Exception as e:
        pass
    else:
        MAX_BULBS_FPS = 10 #if music mode is on, we can update faster
        bulb.duration = (1000/MAX_BULBS_FPS) *2 #to make it less choppy
    bulb.set_rgb(1, 1, 1)


def get_bulb_count() -> int:
    return len(bulbs)

last_update = 0
def update_one_color(rgb:list[int, int, int]):
    global last_update
    if time.time() - last_update < 1/MAX_BULBS_FPS: #too fast, skip
        return
    last_update = time.time()
    for bulb in bulbs:
        h, s, v = tools.RGB_to_HSV(rgb[0], rgb[1], rgb[2])
        bulb.set_hsv(int(h), int(s*100), int(v*100))

def update_bulbs(colors:list[list[int, int, int]], threaded=False):
    global last_update
    '''better use `get_bulb_count()` to know how many colors to parse'''
    if time.time() - last_update < 1/MAX_BULBS_FPS: #too fast, skip
        return
    
    last_update = time.time()
    for index, color in enumerate(colors):
        bulb = bulbs[index]
        h, s, v = tools.RGB_to_HSV(color[0], color[1], color[2])
        if not threaded:
            bulb.set_hsv(int(h), int(s*100), int(v*100))
        else:
            threading.Thread(target=bulb.set_hsv, args=(int(h), int(s*100), int(v*100))).start()


if __name__ == "__main__":
    import time
    while True:
        update_one_color((255, 0, 0))
        time.sleep(1)
        update_one_color((0, 255, 0))
        time.sleep(1)
        update_one_color((0, 0, 255))
        time.sleep(1)