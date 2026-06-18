
from abc import abstractmethod
try:
    from pynput import keyboard
except ImportError:
    print("\a pynput library not found, hotkeys won't work. Install it with 'pip install pynput'")
    keyboard = None

import time
from typing import Callable, TypeVar

try:
    import ctypes  # for detecting caps lock and setting title
    ctypes.windll.kernel32.SetConsoleTitleW("Lights show")
except AttributeError:
    ctypes = None
import threading
import terminal

#all the keys and their corresponding actions
colors = {
    "red": (255, 0, 0),
    "orange": (255, 130, 0),
    "yellow": (255, 220, 0),
    "green": (0, 255, 0),
    "cyan": (0, 255, 200),
    "blue": (0, 0, 255),
    "violet": (128, 0, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}
color_actions = {
    "color 1": colors["red"],
    "color 2": colors["orange"],
    "color 3": colors["yellow"],
    "color 4": colors["green"],
    "color 5": colors["cyan"],
    "color 6": colors["blue"],
    "color 7": colors["violet"],
    "color 8": colors["magenta"],
    "color 9": colors["white"],
    "color 0": colors["black"],
}

actions = {
    "blank": "q",
    "solid": "w",
    "start": "e",
    "end": "r",
    "pulse": "t",
    "strobe": "y",
    "snap": "u",
    "sides": "i",
    "flash": "o",
    "wave": "p",
    "rainbow": "a",
    "pixel chase": "s",
    "fade chase": "d",
    "zoom": "f",
    "alternate": "g",

    "instant mode": "caps_lock",
    "run selected mode": "enter", #covers both
    "store to hotkey": "numpad_decimal",
    "store to hotkey 2": "\\\\",
    
    "slider 0 up": "insert",
    "slider 0 down": "delete",
    "slider 1 up": "home",
    "slider 1 down": "end",
    "slider 2 up": "page_up",
    "slider 2 down": "page_down",

    "+10 BPM": "up",
    "-10 BPM": "down",
    "+1 BPM": "right",
    "-1 BPM": "left",
    "double BPM": ".", #>
    "half BPM": ",", #<

    "pause": "alt_gr",

    "modifier 0": "/",
    "modifier 1": "*",
    "modifier 2": "-",
    "modifier 3": "+",

    "preset 0": "numpad_1",
    "preset 1": "numpad_2",
    "preset 2": "numpad_3",
    "preset 3": "numpad_4",
    "preset 4": "numpad_5",
    "preset 5": "numpad_6",
    "preset 6": "numpad_7",
    "preset 7": "numpad_8",
    "preset 8": "numpad_9",

    "recent 0": "f1",
    "recent 1": "f2",
    "recent 2": "f3",
    "recent 3": "f4",
    "recent 4": "f5",
    "recent 5": "f6",
    "recent 6": "f7",

    
    "recent 7": "f8",
    "recent 8": "f9",
    "recent 9": "f10",
    "recent 10": "f11",
    "recent 11": "f12",
    "clear recents": "esc"
}
actions.update(color_actions)


unknown_keys = {
    97: "numpad_1",
    98: "numpad_2",
    99: "numpad_3",
    100: "numpad_4",
    101: "numpad_5",
    102: "numpad_6",
    103: "numpad_7",
    104: "numpad_8",
    105: "numpad_9",
    96: "numpad_0",
    110: "numpad_decimal",

}

send_to_engine_func: Callable[..., None] = None
def init(send_to_engine: Callable[..., None]):
    global send_to_engine_func
    send_to_engine_func = send_to_engine
    


_pressed_keys = set()
_waiting_to_be_released = set()

def _on_press(key):
    global _pressed_keys
    key_name = str(key).replace("'", "").removeprefix("Key.")

    #unknown codes
    if str(key).startswith("<") and str(key).endswith(">"):
        raw = str(key)[1:-1]
        if raw.isdigit():
            key_name = unknown_keys.get(int(raw), str(key))

    if key_name == "caps_lock": return #managed seperately

    _pressed_keys.add(key_name)
    
def _on_release(key):
    #this is how removing a key works:
    #1. if its a key that is assigned to an action, let the action remove it (that way it will always register the key). 
    #1.1 this does not include keys that are held down by definition, like arrows
    #1.2 if they key was already registered by an action, remove it from the list of keys that are waiting to be released
    #2. if its not an action key, remove it.

    global _pressed_keys, _waiting_to_be_released
    key = str(key).replace("'", "").removeprefix("Key.")
    if str(key).startswith("<") and str(key).endswith(">"):
        if str(key)[1:-1].isdigit():  # Check if it's a number
            key = unknown_keys.get(int(str(key)[1:-1]), str(key))

    if key == "caps_lock": return #managed seperately

    _waiting_to_be_released.discard(key)
    _pressed_keys.discard(key)

def _check_capslock() -> bool:
    '''returns if the caps lock is active, works only on Windows'''
    if ctypes is not None:
        try:
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        except Exception:
            return False
    print("\a Can't check caps lock, ctypes is not important (prob not on Windows)")    
    return False

def is_pressed(key_or_action):
    """
    Checks if a key or action is pressed. Accepts either an action name (from actions) or a key name (e.g., 'f12', 'a', 'left').
    """
    global _pressed_keys, _waiting_to_be_released
    # Try to resolve as action name first
    key = actions.get(key_or_action, key_or_action)
    if isinstance(key, tuple):
        key = key_or_action # it's a number for a color

    if key == "caps_lock":
        return _check_capslock()

    if key in _pressed_keys and key not in _waiting_to_be_released:
        if key not in _waiting_to_be_released:
            _waiting_to_be_released.add(key)
        _pressed_keys.discard(key)
        return True
    elif key not in _pressed_keys and key in _waiting_to_be_released:
        _waiting_to_be_released.discard(key)
    return False

def batched_is_pressed(keys_or_actions:set[str]) -> set[str]:
    """
    Checks if any of the keys or actions in the list are pressed. Returns a list of the ones that are currently pressed.
    """
    return {key for key in keys_or_actions if is_pressed(key)}

def is_held_down(key_or_action):
    """
    Checks if a key or action is currently held down. Accepts either an action name (from actions) or a key name (e.g., 'f12', 'a', 'left').
    """
    global _pressed_keys, actions
    key = actions.get(key_or_action, key_or_action)
    if key == "caps_lock":
        return _check_capslock()
    if key in _pressed_keys:
        return True
    return False

def convert_key_to_action(key):
    """Converts a key name to its corresponding action name, if it exists."""
    for action_name, action_key in actions.items():
        if action_key == key:
            return action_name
    return None

class Keybind:
    def __init__(self):
        self.keys = set()


    def add_key(self, key:str|set[str]):
        '''UPDATING THIS AFTER SUBSCRIBING WOULDN\'T UPDATE THE OBSERVER\'S RELAVENT KEYS, DO IT BEFORE SUBSCRIBING'''
        if isinstance(key, str):
            key = {key}
        self.keys.update(key)
        
    
    def get_keys(self):
        return self.keys
    
    @abstractmethod
    def _update(self, keys:list[str]):
        pass

    @abstractmethod
    def clone(self):
        pass

    @abstractmethod
    def merge(self, src: "Keybind"):
        '''merges another keybind into this one, allowing it to have multiple keys control the same actions'''
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self):
        pass


TKeybind = TypeVar("TKeybind", bound="Keybind")

class KeybindObserver: #each effect would have one of those
    def __init__(self):
        self.keybinds = {} #keybind: (related keys)
        self.relavent_keys = set()

        #for assigning keys, this will be done by this class (sorta factory design pattern)
        self.new_slider_index = 0
        self.new_modifier_index = 0
        self.new_preset_index = 0

    def subscribe(self, keybind:TKeybind) -> TKeybind:
        if isinstance(keybind, Slider):
            keybind._assign_index(self.new_slider_index)
            keybind._assign_keys(f"slider {self.new_slider_index} up", f"slider {self.new_slider_index} down")
            self.new_slider_index += 1
        elif isinstance(keybind, Modifier):
            keybind._assign_key(f"modifier {self.new_modifier_index}")
            self.new_modifier_index += 1
        elif isinstance(keybind, Preset):
            keybind._assign_key(f"preset {self.new_preset_index}")
            self.new_preset_index += 1

        new_keys = keybind.get_keys()
        self.keybinds[keybind] = new_keys
        self.relavent_keys.update(new_keys)

        return keybind #for convenience

    def unsubscribe(self, keybind:Keybind):
        if keybind in self.keybinds:
            keys_to_remove = self.keybinds[keybind]
            self.relavent_keys.difference_update(keys_to_remove)
            del self.keybinds[keybind]
    
    def get_relavent_keys(self):
        return self.relavent_keys

    def update(self, pressed_keys:set[str]):
        for keybind, keys in self.keybinds.copy().items(): #copy cuz the dict might be modified during the loop
            pressed_relavent_keys = pressed_keys.intersection(keys)
            if pressed_relavent_keys:
                keybind._update(pressed_relavent_keys)
    
    def get_keybinds(self) -> list[Keybind]:
        return [k for k in self.keybinds.keys()]

    def __str__(self):
        return "\t".join(list(self.keybinds.keys()))
    
    def clone(self):
        new_observer = KeybindObserver()
        cloned_by_original = {}

        # Clone non-preset keybinds first so Preset references can be remapped
        # to the new Slider/Modifier instances instead of the original observer.
        for keybind in self.keybinds.keys():
            if isinstance(keybind, Preset):
                continue
            cloned = new_observer.subscribe(keybind.clone())
            cloned_by_original[keybind] = cloned

        for keybind in self.keybinds.keys():
            if not isinstance(keybind, Preset):
                continue

            remapped_slider_values = {}
            for slider, value in keybind.slider_values.items():
                cloned_slider = cloned_by_original.get(slider)
                if cloned_slider is None:
                    cloned_slider = new_observer.subscribe(slider.clone())
                    cloned_by_original[slider] = cloned_slider
                remapped_slider_values[cloned_slider] = value

            remapped_modifier_values = {}
            for modifier, value in keybind.modifier_values.items():
                cloned_modifier = cloned_by_original.get(modifier)
                if cloned_modifier is None:
                    cloned_modifier = new_observer.subscribe(modifier.clone())
                    cloned_by_original[modifier] = cloned_modifier
                remapped_modifier_values[cloned_modifier] = value

            cloned_preset = Preset(keybind.name, remapped_slider_values, remapped_modifier_values)
            cloned_preset = new_observer.subscribe(cloned_preset)
            cloned_by_original[keybind] = cloned_preset

        return new_observer
    
    def merge(self, src: "KeybindObserver"):
        #self is the new effect, and src is the one with the valid values
        for src_keybind in src.get_keybinds():
            for dst_keybind in self.get_keybinds():
                if type(src_keybind) == type(dst_keybind):
                    if src_keybind.get_name() == dst_keybind.get_name():
                        dst_keybind.merge(src_keybind)
                        break

    def is_equal(self, other: "KeybindObserver") -> bool:
        if not isinstance(other, KeybindObserver):
            return False
        
        for src_keybind in other.get_keybinds():
            for dst_keybind in self.get_keybinds():
                if type(src_keybind) == type(dst_keybind):
                    if src_keybind.get_name() == dst_keybind.get_name():
                        if dst_keybind.get_value() != src_keybind.get_value():
                            return False
                        break
            else:
                #no matching keybind found
                return False
        return True    

    def get_current_mode_name(self) -> str:
        if self.keybinds == {}:
            return "" #in places like terminal, it will just write the effect name without the mode
        for keybind in self.keybinds.keys():
            if isinstance(keybind, Preset) and keybind.is_active():
                return keybind.get_name()
        return "Custom"
    
    


class Slider(Keybind):
    def __init__(self, name:str, min_value:float, max_value:float, /, step:float=1.0, default_value:float=None):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.default_value = default_value if default_value is not None else (min_value + max_value) / 2
        self.value = self.default_value

        #placeholders
        self.index = 0
        self.up_key = None
        self.down_key = None

        super().__init__()

    def get_value(self) -> float:
        return self.value
    
    def get_name(self) -> str:
        return self.name
    
    def increment(self):
        self.set_value(min(self.value + self.step, self.max_value))
    def decrement(self):
        self.set_value(max(self.value - self.step, self.min_value))

    def set_value(self, value:float):
        self.value = round(max(min(value, self.max_value), self.min_value), ndigits=5)
    
    def reset(self):
        self.value = self.default_value

    def __str__(self):
        return f"{self.name}: {self.value}"
    
    def _assign_keys(self, up_key:str, down_key:str):
        self.up_key = up_key
        self.down_key = down_key
        self.add_key({up_key, down_key})

    def _assign_index(self, index:int):
        self.index = index

    def _update(self, pressed_keys:set[str]):
        #will increment / decrement. if both are pressed, it will reset to default
        up_pressed = self.up_key in pressed_keys
        down_pressed = self.down_key in pressed_keys
        if up_pressed and not down_pressed:
            self.increment()
        elif down_pressed and not up_pressed:
            self.decrement()
        elif up_pressed and down_pressed:
            self.reset()

    def clone(self):
        new_slider = Slider(self.name, self.min_value, self.max_value, self.step, self.default_value)
        new_slider.value = self.value
        return new_slider

    def merge(self, src: "Slider"):
        '''merges another slider into this one, allowing it to have multiple keys control the same slider'''
        self.min_value = src.min_value
        self.max_value = src.max_value
        self.step = src.step
        self.default_value = src.default_value
        self.value = src.value

        self.index = src.index
        self.up_key = src.up_key
        self.down_key = src.down_key
        self.add_key({self.up_key, self.down_key})

class BPM_Slider(Slider):
    #this version is only for one BPM slider instance
    #it breaks some assumptions like not having index / keys
    #the keys are hardcoded (can be changed from the list of actions)
    def __init__(self, default_bpm:int=120):
        super().__init__("BPM", 1, 5000, 1, default_bpm)
        self.add_key({"+10 BPM", "-10 BPM", "+1 BPM", "-1 BPM", "double BPM", "half BPM"})

    def get_value(self):
        return int(super().get_value())
    
    def millis_per_beat(self):
        bpm = self.get_value()
        if bpm == 0:
            return float('inf')
        return 60000 / bpm
    
    def _update(self, pressed_keys:set[str]):
        """
        up: +10 BPM, down: -10 BPM, left: -1 BPM, right: +1 BPM.
        up and down: reset to default
        up and right: multiply
        up and left: divide
        """
        up_pressed = "+10 BPM" in pressed_keys
        down_pressed = "-10 BPM" in pressed_keys
        left_pressed = "-1 BPM" in pressed_keys
        right_pressed = "+1 BPM" in pressed_keys

        double_pressed = "double BPM" in pressed_keys
        half_pressed = "half BPM" in pressed_keys


        if (up_pressed and down_pressed) or (double_pressed and half_pressed):
                self.reset()
        elif double_pressed:
            self.value = min(self.value * 2, self.max_value)
        elif half_pressed:
            self.value = max(self.value / 2, self.min_value)

        elif up_pressed:
            self.value = min(self.value + 10, self.max_value)
        elif down_pressed:
            self.value = max(self.value - 10, self.min_value)
        elif right_pressed:
            self.value = min(self.value + 1, self.max_value)
        elif left_pressed:
            self.value = max(self.value - 1, self.min_value)

        self.value = round(self.value) #just in case, useful for example when dividing it

class Modifier(Keybind):
    def __init__(self, name:str, options_names:list[str] = ["off", "on"], /, default_option:int=0):
        self.name = name
        self.key = None
        self.options = options_names.copy()
        self.default_option = default_option
        self.current_option = self.default_option

        super().__init__()

    def get_option_index(self) -> int:
        return self.current_option
    def get_value(self) -> str:
        return self.options[self.current_option]
    
    def _set_option_index(self, index:int):
        '''sets the current option index, used for cloning'''
        self.current_option = index % len(self.options)
    
    def is_active(self) -> bool:
        '''will return true if index > 0'''
        return self.current_option > 0
    
    def get_name(self) -> str:
        return self.name
    
    def increment(self):
        self.current_option = (self.current_option + 1) % len(self.options)

    def decrement(self):
        self.current_option = (self.current_option - 1) % len(self.options)

    def set_value(self, value:int|str|bool):
        '''
        accepts index, option name or boolean
        '''
        if isinstance(value, bool):
            value = 1 if value else 0
        elif isinstance(value, str):
            if value in self.options:
                value = self.options.index(value)
            else:
                raise ValueError(f"Invalid option name: {value}")
        elif isinstance(value, int):
            value = value % len(self.options)
        
        self.current_option = value

    def reset(self):
        self.current_option = self.default_option

    def __str__(self):
        return f"{self.name}: {self.get_value()}"
    
    def _assign_key(self, key:str):
        self.key = key
        self.add_key(key)
        
    def _update(self, pressed_keys:set[str]):
        if self.key in pressed_keys:
            self.increment()

    def clone(self):
        new_modifier = Modifier(self.name, self.options, self.default_option)
        new_modifier.current_option = self.current_option
        return new_modifier

    def merge(self, src: "Modifier"):
        '''merges another modifier into this one, allowing it to have multiple keys control the same modifier'''
        self.key = src.key
        self.add_key(src.key) #techincally it makes that there are 2 keys, but it doesn't matter it will be filtered
        self.options = src.options
        self.default_option = src.default_option
        self.current_option = src.current_option

class Preset(Keybind):
    def __init__(self, name:str, slider_values:dict[Slider, float|int]={}, modifier_values:dict[Modifier, int|str|bool]={}):
        self.name = name
        self.slider_values = slider_values
        self.modifier_values = modifier_values
        self.key = None

        super().__init__()

    def apply(self):
        for slider, value in self.slider_values.items():
            slider.set_value(value)
        for modifier, index in self.modifier_values.items():
            modifier.set_value(index)

    def get_name(self) -> str:
        return self.name

    def __str__(self):
        return self.get_name()
    
    def _assign_key(self, key:str):
        self.key = key
        self.add_key(key)

    def get_key_name(self) -> str:
        if self.key is None:
            return "Unassigned"
        
        return actions.get(self.key, self.key) #if not found, its prob the key itself

    def _update(self, pressed_keys:set[str]):
        if self.key in pressed_keys:
            self.apply()
        if is_held_down("instant mode"):
            send_to_engine_func()



    def clone(self):
        new_preset = Preset(self.name, self.slider_values.copy(), self.modifier_values.copy())
        new_preset.key = self.key
        return new_preset
    
    def merge(self, src: "Preset"):
        '''Merges another preset values into this one.
        Usesless for Presets because they are already binded to the correct keybinds.
        '''
        pass

    def is_active(self) -> bool:
        for slider, value in self.slider_values.items():
            if slider.get_value() != value:
                return False
        for modifier, index in self.modifier_values.items():

            if isinstance(index, bool): #first check bool, cuz turns out that bool is subclass of int and it messes shit up
                if modifier.is_active() != index: return False
            elif isinstance(index, str):
                if modifier.get_value() != index: return False
            elif isinstance(index, int):
                if modifier.get_option_index() != index: return False

        return True


main_color = (255, 255, 255) #terminal can scream if there is no starting colors
secondary_color = (255, 255, 255)

def set_color(color:tuple[int, int, int]):
    global main_color, secondary_color
    secondary_color = main_color
    main_color = color
    terminal.set_selected_colors(main_color, secondary_color)


def get_main_color() -> tuple[int, int, int]:
    return main_color
def get_secondary_color() -> tuple[int, int, int]:
    return secondary_color
def get_colors() -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    return main_color, secondary_color
    

class GeneralSubject(Keybind):
    def __init__(self, key:str, action:Callable):
        super().__init__()
        self.key = key
        self.action = action
        self.add_key(key)

    def _update(self, pressed_keys:set[str]):
        if self.key in pressed_keys:
            self.action() #if it's an effect class, this line will execute the __init__ of it, and inside it knows to store it as the current selected effect

    def clone(self):
        return GeneralSubject(self.key, self.action)
    
    def merge(self, src: "GeneralSubject"):
        '''merges another GeneralSubject into this one, allowing it to have multiple keys trigger the same action'''
        
        self.key = src.key
        self.add_key(src.key) #techincally it makes that there are 2 keys, but it doesn't matter it will be filtered
        self.action = src.action


class effectKeybind(GeneralSubject):
    def __init__(self, key:str, effect): #can't add type hint cuz of circular import
        super().__init__(key, effect)


general_observer = KeybindObserver() #can be used for actions that should be available always

for i in range(10):
    general_observer.subscribe(GeneralSubject(str(i), lambda color=color_actions[f"color {i}"]: set_color(color)))



BPM = BPM_Slider()
general_observer.subscribe(BPM)

_is_active:bool = True
def toggle_activation():
    global _is_active
    _is_active = not _is_active

def is_active():
    global _is_active
    return _is_active


general_functions:list[Callable] = [] #will be called after each time that any relavent key is pressed

def subscribe_to_general(func:Callable):
    global general_functions
    general_functions.append(func)

TOGGLE_ACTIVATION:Keybind = GeneralSubject("pause", lambda: toggle_activation())
#no subscribe to general cuz it will be checked seperately

_current_observer:KeybindObserver = None

def set_observer(observer:KeybindObserver|None):
    global _current_observer
    _current_observer = observer


def unsubscribe_observer(observer:KeybindObserver|None):
    '''
    unsubscribes the observer, if it is currently subscribed or not observer parsed.
    does nothing if the observer is not subscribed.
    '''
    global _current_observer
    if _current_observer == observer or observer is None:
        _current_observer = None


def _update_observers():
    global _is_active, TOGGLE_ACTIVATION, general_functions
    while True:
        #get all of the interesting keys and check if they were pressed
        relavent_keys:set = general_observer.get_relavent_keys()
        relavent_keys = relavent_keys.union(TOGGLE_ACTIVATION.get_keys())

        if _current_observer is not None:
            relavent_keys = relavent_keys.union(_current_observer.get_relavent_keys())
        pressed_keys = batched_is_pressed(relavent_keys)
        
        if pressed_keys:
            TOGGLE_ACTIVATION._update(pressed_keys) #check if the toggle activation key was pressed, if it was, it will toggle the activation state and not update the observers
            if is_active():
                general_observer.update(pressed_keys)
                if _current_observer is not None:
                    _current_observer.update(pressed_keys)

                for func in general_functions:
                    func()
        time.sleep(0.05)
        
_update_observers_t = threading.Thread(target=_update_observers, daemon=True)

def start_listening():
    global listener
    if keyboard is not None:
        listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        listener.start()  # Runs in background
    _update_observers_t.start()


if __name__ == "__main__":
    start_listening()
    while True:
        print(f"{_pressed_keys=}\t\t{_waiting_to_be_released=}")