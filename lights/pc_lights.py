from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

client = OpenRGBClient()
device = client.devices[0]
def update(rgb_values):
    rgb_values = rgb_values[:len(device.colors)]

    try:
        device.set_colors([RGBColor(*rgb) for rgb in rgb_values], fast=True)
    except Exception as e: 
        pass

def update_one_color(rgb):
    color = RGBColor(*rgb)
    device.set_color(color, fast=True)
    #try:
    #    device.show(fast=True)
    #except Exception as e: pass

def get_pixels_count() -> int:
    return len(device.colors)

if __name__ == "__main__":
    test_rgb_values = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255)  # Magenta
    ]
    update(test_rgb_values)