SEND_TO_ARDUINO = True
SEND_TO_SCREEN = True
SEND_TO_PC_LIGHTS = True
SEND_TO_BULBS = True
SEND_TO_NETWORK = True
MEDIA_UI = True

N_PIXELS = 96
"""Number of pixels in the LED strip"""
HALF_PIXELS = int(N_PIXELS/2) #can be changed to control weird shit
MAX_FPS = 165

ARDUINO_PORT = "COM<port>"  # e.g. "COM3" on Windows or "/dev/ttyUSB0" on Linux
ARDUINO_BAUDRATE = 2000000

BULB_TYPE = "colorb"
BULB_COUNT = 2
MAX_BULBS_FPS = 1



MULTICAST_GROUP = '230.229.228.227'
MULTICAST_PORT = 62192
DATA_PORT = 62193
HEARTBEAT_PORT = 62194

DEFAULT_GAMMA = 2.2

BLACK_FRAME = [[0, 0, 0]] * N_PIXELS

#network handling:
#client broadcasts searching for sender on loop
#once a server found a broadcast, it will immediately recognize it and sends data
#closing: client will close if no data for 1 second (will try to re-search)     server will listen for client's heartbeats, and see if one didn't send for 1 second