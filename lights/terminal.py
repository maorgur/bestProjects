from __future__ import annotations

from typing import Tuple
from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.columns import Columns

import shutil
import keys as keys_lib
import tools

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hotkeys import Hotkey, Recent_observer
    from brain import transition, PreviewEngine




def from_rgb_to_hex(rgb):
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def get_color_name(rgb: list[int]) -> str:
    """Get color name from RGB list, or 'custom' if not in colors dict."""
    for name, color_tuple in keys_lib.colors.items():
        if color_tuple == rgb:
            return name
        
    return "custom" #edge case


def create_select_text(selected_color:list[int]) -> Tuple[Text, str]:
    color_names = list(keys_lib.colors.keys())
    color_index = list(keys_lib.colors.values()).index(tuple(selected_color)) if tuple(selected_color) in keys_lib.colors.values() else -1

    keys = [f"[{"reverse " if color_index==i else ""}{color_names[i]}]{(i+1)%10}: {color_names[i]}[/]" for i in range(10)]

    return Text.from_markup(" ".join(keys), justify="center")

disabled = False #is the program is paused (normal paused, the right alt was pressed)

colors_section = ""
def set_selected_colors(primary: list[int], secondary: list[int]):
    global colors_section
    console = Console(theme=Theme({k:f"rgb{v}".replace(" ", "") for k,v in keys_lib.colors.items()}))
    
    color1_name = get_color_name(primary)
    color2_name = get_color_name(secondary)
    
    with console.capture() as capture:
        primary_style = f"rgb({primary[0]},{primary[1]},{primary[2]})"
        secondary_style = f"rgb({secondary[0]},{secondary[1]},{secondary[2]})"
        
        console.print(Columns(
            [
                Panel(
                    create_select_text(primary),
                    title="Primary color",
                    style=primary_style,
                    height=3,
                    subtitle=color1_name,
                ),
                Panel(
                    create_select_text(secondary),
                    title="Secondary color",
                    style=secondary_style,
                    height=3,
                    subtitle=color2_name
                )
            ], expand=True, equal=True, align="center"
        ))
    colors_section = capture.get()

song_section = ""
def update_song_data(artist_name:str, song_name:str, total_seconds:float, elapsed_seconds:float, playing:bool, platform:str):
    global song_section, disabled
    def seconds_to_hms(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else :
            return f"{minutes}:{seconds:02}"
    
    if not disabled:
        song_percentage = f"\x1b]9;4;1;{int((elapsed_seconds / total_seconds) * 100)}\x07" if total_seconds > 0 and playing else "\x1b]9;4;0\x07"
    else:
        song_percentage = "\x1b]9;4;4;100\x07"

    platform_colors = {
        "spotify": "green",
        "chrome": "yellow",
        "discord": "blue"
    }
    console = Console()
    with console.capture() as capture:
        song_name_text = Text.from_markup(f"[bold yellow]{artist_name}[/]: [cyan]{song_name}[cyan]", justify="left")
        if platform.lower() in platform_colors:
            platform = f"[{platform_colors[platform.lower()]}]{platform.title()}[/]"
        else:
            platform = platform.title()
        bpm_text = Text.from_markup(f"{'[green]playing[/]' if playing else '[red blink]paused[/]'} on {platform}", justify="right")
        bar_length = int(shutil.get_terminal_size().columns) - song_name_text.cell_len - bpm_text.cell_len
        elapsed_text = f"|{seconds_to_hms(elapsed_seconds)}/{seconds_to_hms(total_seconds)}"
        bar_length -= len(elapsed_text) + 1
        bar_length -= 13 #for safety
        if total_seconds - elapsed_seconds < 10:
            elapsed_text = f"[red bold blink]{elapsed_text}[/red bold blink]"
        elif total_seconds - elapsed_seconds < 20:
            elapsed_text = f"[yellow]{elapsed_text}[/yellow]"
        else:
            elapsed_text = f"[green]{elapsed_text}[/green]"
        elapsed_length = round(bar_length * (elapsed_seconds / total_seconds)) if total_seconds > 0 else 0
        left_over_length = bar_length - elapsed_length
        bar = f"[{'green' if playing else 'red'}]{'█' * elapsed_length}[/]{' ' * left_over_length}{elapsed_text}"
        song_bar = Text.from_markup(bar, justify="center")

        song_name_panel = Panel(song_name_text, expand=False, height=3, border_style="yellow")
        song_bar_panel = Panel(song_bar, expand=True, height=3, border_style='green' if playing else 'red' + " bold")
        bpm_panel = Panel(bpm_text, expand=False, height=3, border_style='green' if playing else 'red')
        now_playing_columns = Columns([song_name_panel, song_bar_panel, bpm_panel])

        console.print(now_playing_columns)

    song_section = capture.get()
    song_section += song_percentage
    return




led_strip_section = ""


def _strip_to_ansi(strip: list[list[int]], pixel_width: int) -> str:
    """Convert a strip (RGB list) to an ANSI-colored block string."""
    if not strip:
        return ""
    return (
        "".join(
            f"\033[38;2;{r};{g};{b}m" + ("█" * pixel_width)
            for r, g, b in strip
        )
        + "\033[0m"
    )


def build_led_strip_placeholder(
    strip: list[list[int]],
    max_length: int,
    index: int,
    *,
    pixel_width: int | None = None,
) -> tuple[str, list[list[int]], int]:
    """Build a placeholder string for a strip.

    Args:
        strip: List of [r,g,b] pixels.
        max_length: Max terminal columns available for the strip (in characters).
        index: Placeholder index (e.g. 0 for main, 1..n for layers).
        pixel_width: Optional fixed width (chars) per pixel; if None it's computed.

    Returns:
        (placeholder, downsampled_strip, pixel_width)
    """
    max_length = max(1, int(max_length))
    strip_ds = tools.resize_strip_to_max_size(strip, max_length)
    if pixel_width is None:
        pixel_width = int(max(1, max_length // max(1, len(strip_ds))))

    placeholder_char = str(index)
    placeholder = (
        placeholder_char * (pixel_width * len(strip_ds)) if strip_ds else ""
    )
    return placeholder, strip_ds, pixel_width


def apply_ansi_strip_on_placeholder(
    captured_text: str,
    strip: list[list[int]],
    max_length: int,
    index: int,
    *,
    pixel_width: int | None = None,
) -> str:
    """Find a placeholder in captured text and replace it with an ANSI strip."""
    placeholder, strip_ds, pixel_width = build_led_strip_placeholder(
        strip, max_length, index, pixel_width=pixel_width
    )
    if not placeholder:
        return captured_text

    colored = _strip_to_ansi(strip_ds, pixel_width)
    lines = captured_text.splitlines()
    for idx, line in enumerate(lines):
        if placeholder in line:
            lines[idx] = line.replace(placeholder, colored, 1)
    return "\n".join(lines)


def update_led_strip(main_strip: list[list[int]], layered_strips: list[dict]):
    """Render LED strips.

    We first render placeholder digits with Rich (since Rich objects don't like raw ANSI
    escape sequences inside its elements). After capture (string), we replace the digit
    placeholders with ANSI-colored blocks representing each pixel.

    Placeholders:
      0 -> main strip (sequence of 2*len(main_strip) zeros)
      1..n -> each layered strip line (each digit repeated 2*len(layered_strip_i))
    """
    global led_strip_section

    base_layer_name = layered_strips[0]["name"] if layered_strips else ""
    base_layer_mode_name = layered_strips[0]["mode name"] if layered_strips else ""

    if len(layered_strips) > 1:
        last_layer_name = layered_strips[-1]["name"]
        last_layer_mode_name = layered_strips[-1]["mode name"]
    else:
        last_layer_name = ""
        last_layer_mode_name = ""

    layered_strips = layered_strips[:4]  # Limit to first 4 layers for terminal display

    columns_for_progress_bar = max(1, int(shutil.get_terminal_size().columns) - 5)

    main_placeholder, main_strip_ds, pixel_width = build_led_strip_placeholder(
        main_strip, columns_for_progress_bar, 0
    )

    layer_placeholders: list[str] = []
    layer_frames_ds: list[list[list[int]]] = []
    for i, layer in enumerate(layered_strips):
        ph, frame_ds, _ = build_led_strip_placeholder(
            layer["frame"],
            columns_for_progress_bar,
            i + 1,
            pixel_width=pixel_width,
        )
        layer_placeholders.append(ph)
        layer_frames_ds.append(frame_ds)

    console = Console()
    with console.capture() as capture:
        main_text = Text(main_placeholder, justify="center")
        missing_layers = 4 - len(layer_placeholders)
        padded_layers = "\n".join(layer_placeholders)
        if missing_layers > 0:
            padded_layers += ("\n" + ("#" * len(main_placeholder))) * missing_layers
        layers_text = Text(padded_layers, justify="center") if layer_placeholders else Text("")

        console.print(
            Panel(
                main_text,
                title=base_layer_name,
                height=3,
                subtitle=base_layer_mode_name,
                border_style="bold yellow",
            )
        )
        console.print(
            Panel(
                layers_text,
                title=last_layer_name,
                height=2 + 4,
                subtitle=last_layer_mode_name,
                border_style=" bold green",
            )
        )

    captured = capture.get()
    captured = apply_ansi_strip_on_placeholder(
        captured,
        main_strip_ds,
        columns_for_progress_bar,
        0,
        pixel_width=pixel_width,
    )

    for i, frame_ds in enumerate(layer_frames_ds):
        captured = apply_ansi_strip_on_placeholder(
            captured,
            frame_ds,
            columns_for_progress_bar,
            i + 1,
            pixel_width=pixel_width,
        )

    empty_placeholder = ("#" * len(main_placeholder)) if main_placeholder else ""
    colored_empty = (
        "\033[38;2;0;0;0m" + ("█" * len(main_placeholder)) + "\033[0m"
        if main_placeholder
        else ""
    )

    if empty_placeholder:
        lines = captured.splitlines()
        for idx, line in enumerate(lines):
            if empty_placeholder in line:
                lines[idx] = line.replace(empty_placeholder, colored_empty, 1)
        captured = "\n".join(lines)

    led_strip_section = captured


selected_effect_section = ""
def update_selected_effect(effect_name: str|None, observer: keys_lib.KeybindObserver|None, led_strip: list[list[int]]|None = None):
    global selected_effect_section
    console = Console()
    if effect_name is None or observer is None:
        selected_effect_section = ""
        return
    
    with console.capture() as capture:
        keybinds = observer.get_keybinds()
        result = ""
        if led_strip is not None:
            result += build_led_strip_placeholder(led_strip, shutil.get_terminal_size().columns - 5, 9)[0] + "\n"
        for keybind in keybinds:
            #sliders green, modifiers red
            if isinstance(keybind, keys_lib.Slider):
                result += f"[green]{keybind.get_name()}: [bold]{keybind.get_value()}[/] "
            elif isinstance(keybind, keys_lib.Modifier):
                result += f"[red]{keybind.get_name()}: [bold]{keybind.get_value()}[/] "
            elif isinstance(keybind, keys_lib.Preset):
                if not keybind.is_active():
                    result += f"[blue]{keybind.get_name()}: [bold]{keybind.get_key_name()}[/] "
                else:
                    result += f"[reverse underline blue]{keybind.get_name()}: [bold]{keybind.get_key_name()}[/][/] " #for some reason one is not enough

            else:
                result += f"{str(keybind)} "
    
        console.print(Panel(
            Text.from_markup(result, justify="center"),
            border_style="green",
            title="Effect controls",
            subtitle=effect_name
            )
        )

    before_led_strip_applied = capture.get()
    selected_effect_section = apply_ansi_strip_on_placeholder(before_led_strip_applied, led_strip, shutil.get_terminal_size().columns - 5, 9)

recent_effects_section = ""
def update_recent_effects(recent_effects: Dict[str, "Recent_observer"], hotkey_effects: dict[str, "Hotkey"], selected_effect:"transition", selected_effect_type:type["transition"]|None):
    global recent_effects_section
    console = Console()
    with console.capture() as capture:
        recents_result = " | ".join(f"[yellow {"reverse" if effect_type == selected_effect_type else ""}]{recent_effect.get_name()} [bold]{recent_effect.get_observer().get_current_mode_name()}[/][/]" for effect_type, recent_effect in recent_effects.items())
        #hotkeys_result = " | ".join(f"[dim][cyan {"reverse" if hotkey.is_active(selected_effect_type, selected_effect.get_observer()) else ""}]{key}: [/dim]{hotkey.get_name()} [bold]{hotkey.get_observer().get_current_mode_name()}[/][/]" for index, (key, hotkey) in enumerate(hotkey_effects.items()))
        console.print(Panel(
            Text.from_markup(f"{recents_result}", justify="center"),
            border_style="magenta",
            title="recent effects",
            subtitle="hotkey effects"
            )
        )

    recent_effects_section = capture.get()


hotkeys_preview_section = ""
def update_hotkeys_preview(hotkeys: dict[str, dict[str, Hotkey|PreviewEngine]], to_be_deleted_index: int|None = None, selected_effect:"transition" = None, selected_effect_type:type["transition"]|None = None):
    global hotkeys_preview_section
    console = Console()
    #pre-compute the strips for all hotkeys to avoid doing it multiple times in the loop below
    strips = [hotkey["preview"].update() if hotkey["hotkey"] is not None and hotkey["preview"] is not None else None for hotkey in hotkeys.values()]
    
    with console.capture() as capture:
        for index, (kb_key, value) in enumerate(hotkeys.items()):
            hotkey = value["hotkey"]
            if hotkey is None or strips[index] is None:
                continue


            strip_placeholder = build_led_strip_placeholder(strips[index], shutil.get_terminal_size().columns - 5, index + 1)[0]
            console.print(Panel(
                Text.from_markup(strip_placeholder, justify="center"),
                title=hotkey.get_full_name(),
                subtitle=kb_key,
                border_style=("cyan" if index != to_be_deleted_index else "red") + " reverse" if hotkey.is_active(selected_effect_type, selected_effect.get_observer()) else ("cyan" if index != to_be_deleted_index else "red")
            ))
    before_led_strip_applied = capture.get()
    for index, (kb_key, hotkey) in enumerate(hotkeys.items()):
        
        if hotkey["hotkey"] is None or strips[index] is None:
            continue
        before_led_strip_applied = apply_ansi_strip_on_placeholder(before_led_strip_applied, strips[index], shutil.get_terminal_size().columns - 5, index + 1)
    
    hotkeys_preview_section = before_led_strip_applied



information_section = ""
def update_information(bpm:int, fps:int, is_paused:bool, is_immediate_mode:bool):
    global information_section, disabled
    disabled = is_paused
    console = Console()
    with console.capture() as capture:
        if bpm > 0 and fps > 0:
            frames_per_beat = (60 / bpm) * fps
        else:
            frames_per_beat = 0
        status = "[red blink]PAUSED[/]" if is_paused else "[green]ACTIVE[/]"
        immediate_mode_status = " [bold reverse blue]IMMEDIATE MODE[/] |" if is_immediate_mode else "[bold blue] Normal mode[/] |"
        console.print(
            Text.from_markup(
                f"Status: {status} |{immediate_mode_status} BPM: [bold yellow]{bpm}[/] | FPS: [bold yellow]{fps}[/] | Frames per beat: [bold yellow]{frames_per_beat:.2f}[/]",
                justify="center",
                end=""
            ),end=""
        ),
    information_section = capture.get()

def init(main=True):
    if main: set_selected_colors([255, 255, 255], [255, 255, 255])
    print('\033[?25l', end="")

last_terminal_size = (0,0)
def print_terminal():
    global last_terminal_size
    current = shutil.get_terminal_size()
    current_size = (current.columns, current.lines)

    parts = ["\033[H"]  # Move cursor to top-left
    if current_size != last_terminal_size:
        parts.append("\033[2J")  # Clear entire screen
        last_terminal_size = current_size

    parts.append(colors_section)
    if current_size[1] > 15:
        parts.append(led_strip_section)
    parts.append(selected_effect_section)
    parts.append(recent_effects_section)
    parts.append(hotkeys_preview_section)
    parts.append(information_section)
    parts.append("\x1b[J")  # Clear from cursor to end of screen
    gap = current_size[1] - "".join(parts).count("\n") - song_section.count("\n") - 4 #4 is the number that just works, idk might need to be changed
    parts.append("\n" * max(0, gap))
    parts.append(song_section.removesuffix("\n"))

    print("".join(parts), end="")
