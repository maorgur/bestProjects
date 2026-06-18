import threading

from config import *
import time
import keys
from abc import ABC, abstractmethod
import terminal
import hotkeys
import tools
if MEDIA_UI: import media_controller
if SEND_TO_SCREEN:
    import screen
    screen.start_window()

if SEND_TO_ARDUINO: 
    import raw_serial
    arduino = raw_serial.LEDController()

if SEND_TO_PC_LIGHTS:
    import pc_lights
    pc_lights_amount = pc_lights.get_pixels_count()

if SEND_TO_BULBS:
    import light_bulbs
    BULB_COUNT = light_bulbs.get_bulb_count()

if SEND_TO_NETWORK:
    import broadcaster
    broadcaster.init()

#i have to initialize it here bcs when simpleTransition is created, this needs to be used
configurating_effect = None
configurating_effect_type = None
def set_configurating_effect(effect: type["transition"], /, set_by_hotkey=False) -> "transition": #note that it's being used also by keys.Hotkey
    '''this function should receive an uninitialized effect!'''
    global configurating_effect, configurating_effect_type
    configurating_effect_type = effect
    configurating_effect = effect()
    hotkeys.effect_was_selected(effect, configurating_effect, set_by_hotkey=set_by_hotkey)
    configurating_preview_engine.set_transition(configurating_effect)
    return configurating_effect

def send_configurating_effect_to_engine():
    global configurating_effect
    if configurating_effect is not None:
        #copy over the observer
        configurating_effect_temp = configurating_effect_type()
        transition_engine.append_transition(configurating_effect)

        
        if configurating_effect.get_observer() is not None:
            configurating_effect_temp._set_observer(configurating_effect.get_observer().clone())
            configurating_effect = configurating_effect_temp
            configurating_preview_engine.set_transition(configurating_effect)
        
        hotkeys.effect_was_sent(configurating_effect, configurating_effect_type, set_configurating_effect)
        configurating_effect._re_apply_observer() #cuz of the prev line accidently subbing it's observer for the preview


def send_configurating_effect_to_hotkeys():
    global configurating_effect
    if configurating_effect is not None:
        hotkeys.effect_was_sent(configurating_effect, configurating_effect_type, set_configurating_effect)
        configurating_effect._re_apply_observer() #cuz of the prev line accidently subbing it's observer for the preview


class transition(ABC):
    '''
    Base class for all effects, should be inherited.
    for a basic template, see simpleTransition.
    '''
    def __init__(self, name:str, /, observer:keys.KeybindObserver=None, beats_duration=1):
        '''
        name: name of the transition, used for debugging and visualization.
        observer: (optional) should store all of the modifiers and sliders for this transition.
        beats_duration: (default 1) the length of a lap of the effect in beats. For example if the BPM is 120, and the beats_duration is 3, the lap will be 1.5 seconds long.
        '''
        self.observer = observer if observer is not None else keys.KeybindObserver()
        self.start_time = None
        self.name = name
        self.active = False
        self.duration = beats_duration
        self.base = True

        self.effect_bpm_in_ms = keys.BPM.millis_per_beat()

        keys.set_observer(self.observer)

    def start(self, /, beats_duration=None):
        '''
        This function will be executed when the effect is sent to the engine and running. it wouldn't be called on every lap, only at the start of the first lap.
        You can also change the `beats_duration` if needed.
        This function can be overriden, just make sure to execute the super function at the start.
        '''
        if beats_duration is not None:
            self.duration = beats_duration

        self.effect_bpm_in_ms = keys.BPM.millis_per_beat()
        self.start_time = time.time()
        self.absolute_start_time = self.start_time
        self.active = True

    def end(self):
        '''
        When `end` is called, the effect will be removed immediately from the engine, you should call it when it's relavent.
        This function can be overriden, just make sure to execute the super function somewhere.
        '''
        self.active = False

    def finished_lap(self):
        '''
        Every time a lap is completed, the engine will execute this function.
        This function can be overriden, just make sure to execute the super function somewhere.
        '''
        self.start_time = time.time()

    def is_running(self) -> bool:
        '''
        Whether the effect is still active, the returned value can be controlled with `start` and `end`
        This function can be overriden.
        '''
        return self.active

    def get_progress(self)-> float:
        '''
        Return a float between 0 and 1 representing the percentage of the current lap that has elapsed.
        You should use this function when generating a frame for a non-static effect.
        This function shouldn't be overriden, it's being used by the engine to check if a lap is finished.
        '''
        if not self.is_running() or self.duration == 0: #for no start_time returns 1 cuz it helps with getting the last frame of a finished effect
            return 1
        
        total_length = self.effect_bpm_in_ms * self.duration
        elapsed = (time.time() - self.start_time) * 1000
        return min(elapsed / total_length, 1)
    
    def get_absolute_progress(self) -> float:
        '''
        Like `get_progress`, but it returns the percentage of the lap that has elapsed since the effect was started, it can surpass 1.
        This function shouldn't be overriden, although there is no risk of doing so.
        '''
        if not self.is_running() or self.duration == 0:
            return 1
        
        total_length = self.effect_bpm_in_ms * self.duration
        elapsed = (time.time() - self.absolute_start_time) * 1000
        return elapsed / total_length
    

    @abstractmethod
    def get_frame(self, previous_frame, current_frame) -> list[list[int, int, int]]:
        """
        Main function: based on the given previous and current frames and more data as you like (for example the elapsed percentage), return a new frame.
        There is no gurantee that the frame created is directly for showing on the strip, and the paramaters can change suddenly at any point for different needs (like showing the effect alone for the UI).
        This function MUST be overriden, and it's being used by the engine.
        """
        pass
    
    def get_base(self) -> bool:
        """Whether this transition is a base transition (replaces the entire strip) or an overlay"""
        return self.base
    
    def set_base(self, value: bool):
        """Set whether this transition is a base transition (replaces the entire strip) or an overlay"""
        self.base = value

    def get_name(self) -> str:
        """Return the name of the transition, used for visualization."""
        return self.name
    
    def get_observer(self) -> keys.KeybindObserver:
        """Return the observer of the transition, used for getting the modifiers and sliders for this transition."""
        return self.observer
    
    def _set_observer(self, observer: keys.KeybindObserver):
        """For internal use inside the `brain` module, will be used to copy effects so they have the same configs"""
        if self.observer is None:
            self.observer = observer
        else:
            self.observer.merge(observer)
    
    def _re_apply_observer(self):
        """
        If for some reason the observer was unsubscribed (prob because of hotkey previews initializing)m this will re-apply the observer
        """
        keys.set_observer(self.observer)
        

class simpleTransition(transition):
    def __init__(self, /, frame=None, color=None):
        self.color = color
        self.frame = frame if frame is not None else [self.color] * N_PIXELS
        super().__init__("Simple Transition", beats_duration=0)

    def start(self):
        if self.frame is None:
            self.frame = [self.color]*N_PIXELS if self.color is not None else [keys.get_main_color()] * N_PIXELS
        super().start()

    def get_frame(self, previous_frame, current_frame):
        return self.frame

class TransitionEngine:
    """
    Core transition manager.
    Maintains a stack/list of active transitions (base + overlays), advances them,
    composites frames, handles repeating logic, and exposes layered frames for
    debugging / visualization. Designed to be agnostic of the final rendering
    target (LED strip, screen, etc.).
    """
    def __init__(self):
        self.previous_frame:list[list[int, int, int]] = BLACK_FRAME  # Updated only when a base transition finishes
        self.current_frame:list[list[int, int, int]] = BLACK_FRAME
        self.append_transition(simpleTransition(color = [0,0,0])) #start with a simple transition to have a base frame to work with
        self.active_transitions:list[transition]

    def append_transition(self, new_transition: transition):
        new_transition.start() #activate before bcs maybe the effect will change if it's a base or not here
        if new_transition.get_base():
            self.previous_frame = self.current_frame.copy() #update the previous frame to the current frame before starting the new base transition
            self.active_transitions = [new_transition]
            
        else:
            self.active_transitions.append(new_transition)

    def handle_finished_transitions(self):
        global configurating_effect
        to_remove = []
        for index, transition in enumerate(self.active_transitions):

            if transition.get_progress() >= 1: #tell it that it's finished a lap
                transition.finished_lap()

            if not transition.is_running(): #check if one of the effects decided to finish

                if not transition.get_base(): 
                    to_remove.append(transition)
                else: #if it's a base transition, update the previous frame to the current frame
                    #there should always be a base effect (if not a non base might be mistaken for a base)
                    self.active_transitions[0] = simpleTransition(frame = transition.get_frame(self.previous_frame, BLACK_FRAME.copy())) #update the base transition to a simple transition with the final frame of the finished transition, so the next transitions will use the final frame as previous frame and not the one from the last lap
                    self.active_transitions[0].start()

                    #fixed bug: simple transition cleans the observer, so it needs to be re-applied
                    configurating_effect._re_apply_observer()

                    #edge case: the effect might set itself as base after starting (for example zoom)
                    if index != 0:
                        #delete all effects below it
                        for t in self.active_transitions[1:index+1]:
                            to_remove.append(t)
                

        for transition in to_remove:
            self.active_transitions.remove(transition)
            
    def update(self) -> list[list[int, int, int]]:
        #self.current_frame = BLACK_FRAME.copy() #start with a black frame, then add the effects on top of it
        for t in self.active_transitions:
            self.current_frame = t.get_frame(self.previous_frame.copy(), self.current_frame.copy())

        self.handle_finished_transitions() #handle at the end so effects can reach their final frame before getting deleted or something
        return self.current_frame


    def get_layers(self) -> list:
        """
        Return a list of layer dictionaries for each active transition.
        Each dict contains:
            name: transition name (str)
            modifiers: list of modifier strings
            frame: the per‑transition frame (list[list[int, int, int]])
        Base transitions get composed using previous/current history.
        Non‑base transitions are rendered in isolation (black background).
        """
        layers = []
        for t in self.active_transitions:
            name, modifiers = t.get_name(), [str(x) for x in t.get_observer().get_keybinds() if not isinstance(x, keys.Preset)]
            if t.get_base():
                frame = t.get_frame(self.previous_frame.copy(), self.current_frame.copy())
            else:
                frame = t.get_frame(BLACK_FRAME.copy(), BLACK_FRAME.copy())
            layers.append({
                "name": name,
                "modifiers": modifiers,
                "frame": frame,
                "mode name": t.get_observer().get_current_mode_name() if t.get_observer() else None
            })
        return layers
    
class PreviewEngine():
    """
    A simplified version of TransitionEngine that only renders one transition at a time on forced loop, used for the UI preview.
    """
    def __init__(self):
        self.current_transition = None
        keys.subscribe_to_general(self.force_start_transition)

    def set_transition(self, transition: transition):
        self.current_transition = transition
        self.current_transition.start()

    def handle_finished_transition(self):
        if self.current_transition is not None and self.current_transition.get_progress() >= 1:
            self.current_transition.finished_lap()
            if not self.current_transition.is_running():
                self.current_transition.start() #force loop

    def update(self) -> list[list[int, int, int]]:
        if self.current_transition is None:
            return BLACK_FRAME.copy()
        
        self.handle_finished_transition()
        return self.current_transition.get_frame(BLACK_FRAME.copy(), BLACK_FRAME.copy())
    
    def force_start_transition(self):
        if self.current_transition is not None:
            self.current_transition.start()

    def clear(self):
        self.current_transition = None


transition_engine = TransitionEngine()
configurating_preview_engine = PreviewEngine()

frame = BLACK_FRAME.copy() #placeholder
layered_frames = [{"name": "", "modifiers": [], "frame": frame, "mode name": ""}] #placeholder

def print_to_terminal_on_loop():
    global current_fps, configurating_effect, configurating_effect_type
    while True:
        terminal.update_led_strip(frame, layered_frames)
        terminal.update_information(keys.BPM.get_value(), current_fps, not keys.is_active(), keys.is_held_down("instant mode"))
        terminal.update_selected_effect(configurating_effect.get_name() if configurating_effect else "None", configurating_effect.get_observer() if configurating_effect else None,
                                        configurating_preview_engine.update())
        terminal.update_recent_effects(*hotkeys.get_recent_and_hotkey_effects(), configurating_effect, configurating_effect_type)
        terminal.update_hotkeys_preview(hotkeys.get_recent_and_hotkey_effects()[1], hotkeys.get_to_delete_hotkey_index(), configurating_effect, configurating_effect_type)


        terminal.print_terminal()

        time.sleep(0.001)



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

def update_network_on_loop():
    while True:
        broadcaster.send_frame(frame)
        time.sleep(1/MAX_FPS)

def update_arduino_on_loop():
    while True:
        arduino.send_frame(frame)

        time.sleep(0.001) #unlock the GIL



def update_constantly():
    
    global current_fps, configurating_effect, configurating_effect_type, previous_update, frame, layered_frames
    last_frame_update = time.time()
    previous_update = time.time()
    current_fps = 0
    current_frames = 0

    keys.init(send_configurating_effect_to_engine)

    keys.general_observer.subscribe(keys.GeneralSubject("run selected mode", send_configurating_effect_to_engine))
    #2 different keys for the same thing:
    keys.general_observer.subscribe(keys.GeneralSubject("store to hotkey", send_configurating_effect_to_hotkeys))
    keys.general_observer.subscribe(keys.GeneralSubject("store to hotkey 2", send_configurating_effect_to_hotkeys))

    if MEDIA_UI:
        media_controller.start_report_to_terminal_thread()

    threading.Thread(target=print_to_terminal_on_loop, daemon=True).start()
    if SEND_TO_ARDUINO:
        threading.Thread(target=update_arduino_on_loop, daemon=True).start()
    
    if SEND_TO_PC_LIGHTS:
        threading.Thread(target=update_pc_lights_on_loop, daemon=True).start()

    if SEND_TO_BULBS:
        threading.Thread(target=update_light_bulbs_on_loop, daemon=True).start()

    if SEND_TO_NETWORK:
        threading.Thread(target=update_network_on_loop, daemon=True).start()

    hotkeys.init(PreviewEngine, send_configurating_effect_to_engine)

    terminal.init()
    while True:
        frame = transition_engine.update()
        layered_frames = transition_engine.get_layers()

        if SEND_TO_SCREEN: #non blocking code
            screen.set_colors(frame)


        current_frames += 1

        current_time = time.time()

        if current_time - last_frame_update > 1:
            current_fps = current_frames
            current_frames = 0
            last_frame_update = current_time

        if current_time - previous_update < 1/MAX_FPS:
            time.sleep((1/MAX_FPS) - (current_time - previous_update))

        previous_update = current_time


