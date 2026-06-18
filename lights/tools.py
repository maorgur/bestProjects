'''
This file contains some useful functions to be used in effects that want to
'''
import colorsys
import config

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def fade_color(color1:list[int], color2:list[int], weight:float):
    '''
    Returns a color that is a weighted average of the two input colors.
    When weight is 0, the result is color1, when weight is 1, the result is color2.
    '''
    return [int(color1[i] * (1 - weight) + color2[i] * weight) for i in range(3)]

def fade_frames(frame1:list[list[int]], frame2:list[list[int]], weight:float):
    '''
    Returns a frame that is a weighted average of the two input frames.
    When weight is 0, the result is frame1, when weight is 1, the result is frame2.
    '''
    return [fade_color(frame1[i], frame2[i], weight) for i in range(len(frame1))]

def pulsing_progress(progress:float) -> float:
    '''
    Converts a linear progress value (0 to 1) into a pulsing progress value that goes from 0 to 1 and back to 0.
    '''

    if progress < 0.5:
        return progress * 2
    else:
        return (1 - progress) * 2

def circular_distance(a:float, b:float, modulo:float|int=1, b_is_right_to_a:bool=False) -> float:
    """Calculates the circular distance between two values a and b, given a modulo."""
    direct_distance = abs(a - b)
    wrap_around_distance = modulo - direct_distance
    if not b_is_right_to_a:
        return min(direct_distance, wrap_around_distance)
    else:
        if (a<b): return direct_distance
        else: return wrap_around_distance

def crop_progress(progress:float, start:float, end:float) -> float:
    """Trims a progress value so it will go up from `start` and end at `end`, if progress it too early it will return 0, if it's too late it will return 1."""
    if progress < start:
        return 0
    elif progress > end:
        return 1
    else:
        return (progress - start) / (end - start)
    
def symmetric_crop_progress(progress:float, width:float) -> float:
    if width >= 1:
        return progress
    return crop_progress(progress, (1 - width) / 2, 1 - (1 - width) / 2)

def fade_from_previous_frame(previous_frame:list[list[int]], new_frame:list[list[int]], absolute_progress:float, progress_multiplier:float=1) -> list[list[int]]:
    """
    Parse the `previous_frame` provided from `get_frame` and the `absolute_progress` from `get_absolute_progress`.
    If the effect length is not 1 beat, u can tell that in `progress_multiplier`, if for example it's 2 beats, parse 0.5.
    """
    progress = clamp(absolute_progress * progress_multiplier, 0, 1)
    return fade_frames(previous_frame, new_frame, progress)

def _smoothstep(x):
    return x * x * (3 - 2 * x)

def blob_of_color(
    frame:list[list[int]], 
    color:list[int], 
    start_position: float, 
    pixels_count: float = None, 
    blend_with_other_colors: bool = True, 
    border_width = 0.0,  # can be float or (float, float)
    end_position: float = None, 
    circular: bool = False, 
    smooth: bool = True,
    fade: float = 1.0,  # 0-1
    mask: list = None,  # list of 0-255 values
    pixels_include_borders: bool = False  # if True, pixels_count includes borders
):
    frame_size = len(frame)
    # parse border_width
    if isinstance(border_width, (tuple, list)) and len(border_width) == 2:
        border_start, border_end = border_width
    else:
        border_start = border_end = border_width

    if end_position is not None:
        if pixels_include_borders:
            # end_position is the end of the whole blob (borders included)
            total_length = end_position - start_position
            pixels_count = max(0, total_length - border_start - border_end)
        else:
            # end_position is the end of the solid region (borders outside)
            pixels_count = end_position - start_position - border_start - border_end
    elif pixels_count is not None:
        if pixels_include_borders:
            # pixels_count is the total length (borders included)
            end_position = start_position + pixels_count
            pixels_count = max(0, pixels_count - border_start - border_end)
        else:
            # pixels_count is the solid region (borders outside)
            end_position = start_position + border_start + pixels_count + border_end
    else:
        raise ValueError("Must provide either pixels_count or end_position")

    fade = clamp(fade, 0.0, 1.0)

    frame = frame.copy()

    for p in range(frame_size):
        pixel_pos = p

        # mask check
        if mask:
            mask_value = mask[p]
            if mask_value <= 0:
                continue
            mask_factor = mask_value / 255.0
        else:
            mask_factor = 1.0

        # handle circular logic
        if circular:
            rel_pos = (pixel_pos - start_position + frame_size) % frame_size
            inside = rel_pos >= 0 and rel_pos < (border_start + pixels_count + border_end)
        else:
            rel_pos = pixel_pos - start_position
            inside = rel_pos >= 0 and rel_pos < (border_start + pixels_count + border_end)

        if not inside:
            continue

        # determine blend factor for each side
        if rel_pos < border_start:
            # Start border
            if border_start == 0:
                blend_factor = 1.0
            else:
                blend_factor = rel_pos / border_start
        elif rel_pos >= border_start + pixels_count:
            # End border
            dist_end = rel_pos - (border_start + pixels_count)
            if border_end == 0:
                blend_factor = 1.0
            else:
                blend_factor = 1.0 - (dist_end / border_end)
        else:
            # Solid region
            blend_factor = 1.0

        if smooth:
            blend_factor = _smoothstep(blend_factor)

        blend_factor *= fade * mask_factor

        if blend_factor <= 0.0:
            continue

        if blend_with_other_colors:
            frame[p] = fade_color(frame[p], color, blend_factor)
        else:
            if blend_factor >= 1.0:
                frame[p] = color
            else:
                # Ignore current pixel color and blend from black.
                frame[p] = fade_color([0, 0, 0], color, blend_factor)

    return frame

def HSV_to_RGB(hue:float, saturation:float, value:float) -> list[int]:
    """Converts HSV color to RGB color. Hue is 0-360, saturation and value are 0-1."""
    r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, value)
    return [int(r * 255), int(g * 255), int(b * 255)]

def RGB_to_HSV(r:int, g:int, b:int) -> list[float]:
    """Converts RGB (0-255) to HSV. Returns [hue 0-360, saturation 0-1, value 0-1]."""
    # normalize to 0-1 for colorsys
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    h, s, v = colorsys.rgb_to_hsv(rf, gf, bf)
    return [h * 360.0, s, v]

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def resize_strip_to_size(strip: list[list[int]], target_pixel_count: int) -> list[list[int]]:

    n = len(strip)
    if n == target_pixel_count:
        return strip

    # Nearest-neighbor resampling.
    # - If shrinking, picks evenly-spaced indices from the original.
    # - If growing, repeats pixels as needed.
    if target_pixel_count == 1:
        return [strip[n // 2]]

    denom = target_pixel_count - 1
    return [strip[(i * (n - 1) + denom // 2) // denom] for i in range(target_pixel_count)]

def resize_strip_to_max_size(strip: list[list[int]], max_pixels: int) -> list[list[int]]:
    """Downsample strip by taking every Nth pixel so it fits max_pixels."""
    if max_pixels <= 0 or len(strip) <= max_pixels:
        return strip
    step = (len(strip) + max_pixels - 1) // max_pixels
    return strip[::step][:max_pixels]

# Precompute gamma correction table once
def make_gamma_table(gamma=config.DEFAULT_GAMMA):
    return [
        int(((i / 255.0) ** gamma) * 255 + 0.5)
        for i in range(256)
    ]


# Create the table
GAMMA_TABLE = make_gamma_table()

def gamma_correction(color:list[int, int, int]) -> list[int, int, int]:
    """Applies gamma correction to a color using the precomputed GAMMA_TABLE."""
    return [
        GAMMA_TABLE[clamp(int(color[0]), 0, 255)],
        GAMMA_TABLE[clamp(int(color[1]), 0, 255)],
        GAMMA_TABLE[clamp(int(color[2]), 0, 255)]
    ]

def batch_gamma_correction(frame:list[list[int, int, int]]) -> list[list[int, int, int]]:
    """Applies gamma correction to an entire frame."""
    return [gamma_correction(pixel) for pixel in frame]