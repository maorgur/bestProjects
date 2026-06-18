"""Raw binary LED frame sender matching the Arduino fast protocol.

Protocol:
- Sender writes: '>' (0x3E) + N*3 raw bytes (RGB order), where N=REQUIRED_SIZE.
- Device replies with a line "RDY" after applying the frame.
"""

import serial
from config import N_PIXELS, ARDUINO_PORT, ARDUINO_BAUDRATE
import tools

# Must match Arduino NUM_LEDS (default 120). Adjust if your strip length differs.
REQUIRED_SIZE = N_PIXELS


class LEDController:
    def __init__(self, port: str|None=None, baud_rate: int|None=None):
        """Initialize the serial connection to the microcontroller."""
        if port is None: port = ARDUINO_PORT
        if baud_rate is None: baud_rate = ARDUINO_BAUDRATE
        self.ser = serial.Serial(port, baud_rate, timeout=0.2)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def send_frame(self, rgb_list):
        """Send one frame and wait for the 'RDY' response for flow control."""
        try:
            rgb_list = self._make_data_the_right_size(rgb_list)
            rgb_list = tools.batch_gamma_correction(rgb_list)
        
            # Build binary payload: '>' + raw RGB bytes
            payload = bytearray(1 + REQUIRED_SIZE * 3)
            payload[0] = ord('>')
            idx = 1
            for r, g, b in rgb_list:
                payload[idx] = r & 0xFF
                payload[idx + 1] = g & 0xFF
                payload[idx + 2] = b & 0xFF
                idx += 3

            # Send and wait for RDY ('b'1')
            self.ser.write(payload)
            line = self.ser.read()
            # If not RDY (e.g., partial echo/noise), keep reading until RDY or small timeout
            attempts = 0
            while line != b'1' and attempts < 4:
                line = self.ser.read()
                attempts += 1
        except Exception as e:
            print(f"Serial error: {e}")

    def _make_data_the_right_size(self, data):
        """Pad/crop to REQUIRED_SIZE and clamp values."""
        # Pad with zeros if too small
        if len(data) < REQUIRED_SIZE:
            data = list(data) + [[0, 0, 0]] * (REQUIRED_SIZE - len(data))
        # Cut if too large
        data = data[:REQUIRED_SIZE]
        # Clamp RGB values to 0-255 and print a warning if out of bounds
        for i, (r, g, b) in enumerate(data):
            nr = 0 if r is None else int(r)
            ng = 0 if g is None else int(g)
            nb = 0 if b is None else int(b)
            nr2 = min(max(nr, 0), 255)
            ng2 = min(max(ng, 0), 255)
            nb2 = min(max(nb, 0), 255)
            if (nr, ng, nb) != (nr2, ng2, nb2):
                print(
                    f"Warning: Pixel {i} RGB out of bounds. Clamped from ({nr},{ng},{nb}) to ({nr2},{ng2},{nb2})"
                )
            data[i] = [nr2, ng2, nb2]
        return data

