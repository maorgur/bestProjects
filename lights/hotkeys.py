import keys
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from brain import transition, PreviewEngine

HOTKEYS_LIMIT = 8
recent_effects: dict[type["transition"], Recent_observer] = {}
hotkey_effects: dict[str, dict[str, Hotkey|PreviewEngine]] = {}

#immediate mode
send_to_engine_func: Callable[..., None] = None


def init(preview_engine_class: type[PreviewEngine], send_to_engine: Callable[..., None]):
    global recent_effects, hotkey_effects, send_to_engine_func
    recent_effects = {}
    hotkey_effects = {f"f{index+1}":{"hotkey": None, "preview":preview_engine_class()} for index in range(HOTKEYS_LIMIT)}

    keys.general_observer.subscribe(keys.GeneralSubject("clear recents", lambda: clear_hotkeys()))

    send_to_engine_func = send_to_engine



def clear_hotkeys():
    global hotkey_effects, next_hotkey_index
    for key, value in hotkey_effects.items():
        if value["hotkey"] is not None:
            value["hotkey"].unsubscribe()
            value["hotkey"] = None
        value["preview"].clear()
    next_hotkey_index = 0
    
next_hotkey_index = 0 #range of 0-11
class Hotkey(keys.Keybind):
    def __init__(self, set_configurating_effect_func:Callable[..., "transition"], uninitialized_effect:Callable[..., "transition"], observer:keys.KeybindObserver, name:str):
        global next_hotkey_index

        super().__init__()
        self.index = next_hotkey_index

        self.key = f"recent {next_hotkey_index}"
        next_hotkey_index = (next_hotkey_index + 1)%HOTKEYS_LIMIT
        self.add_key(self.key)

        self.func = set_configurating_effect_func
        self.unintialized_effect = uninitialized_effect
        self.observer = observer

        self.name = name

        #delete old one on the same key
        if hotkey_effects[self.get_key()]["hotkey"] is not None:
            hotkey_effects[self.get_key()]["hotkey"].unsubscribe()
            del hotkey_effects[self.get_key()]["hotkey"]
        #add this
        hotkey_effects[self.get_key()]["hotkey"] = self

        preview_engine = hotkey_effects[self.get_key()]["preview"]
        preview_engine.set_transition(self.create_initialized_effect())

    def _update(self, pressed_keys: set[str]):
        global next_hotkey_index

        if self.key in pressed_keys:
            #run
            initialized_effect = self.func(self.unintialized_effect, set_by_hotkey=True)
            initialized_effect._set_observer(self.observer)

            send_to_engine_func() #even if instant mode is off

            #if it's almost deleted, skip it cuz it's being used
            if self.index == next_hotkey_index:
                next_hotkey_index = (next_hotkey_index + 1)%HOTKEYS_LIMIT


    def get_unitialized_effect(self) -> Callable:
        return self.unintialized_effect
    
    def get_observer(self) -> keys.KeybindObserver:
        return self.observer
    
    def get_key(self) -> str:
        '''returns the key as a keyboard key, not action name'''
        return keys.actions.get(self.key, self.key) #if not found, its prob the key itself
    
    def get_name(self) -> str:
        return self.name
    
    def get_full_name(self) -> str:
        if not self.observer.get_current_mode_name():
            return self.get_name()
        else:
            return f"{self.get_name()} - {self.observer.get_current_mode_name()}"

    def clone(self) -> "Hotkey":
        return Hotkey(self.func, self.unintialized_effect, self.observer.clone())
    
    def merge(self, src: "Hotkey"):
        pass #useless for hotkey

    def is_equal(self, other: "Hotkey") -> bool:
        if not isinstance(other, Hotkey): return False
        if self.unintialized_effect != other.unintialized_effect: return False
        if not self.observer.is_equal(other.observer): return False
        return True
    
    def is_active(self, current_unitialized_effect, current_observer) -> bool:
        if self.unintialized_effect != current_unitialized_effect: return False
        if not self.observer.is_equal(current_observer): return False
        return True
    
    def create_initialized_effect(self) -> "transition":
        """
        DANAGER: this has an unwanted side effect of subscribing this hotkey's observer, make sure it re-subscribe the original one back.
        """
        initialized_effect = self.unintialized_effect()
        initialized_effect._set_observer(self.observer)
        return initialized_effect
    
    def unsubscribe(self):
        global hotkey_effects
        keys.general_observer.unsubscribe(self)
    
class Recent_observer:
    def __init__(self, observer:keys.KeybindObserver, name:str):
        self.observer = observer
        self.name = name
    
    def get_observer(self) -> keys.KeybindObserver:
        return self.observer
    
    def set_observer(self, observer:keys.KeybindObserver) -> None:
        self.observer = observer

    def get_name(self) -> str:
        return self.name


def effect_was_selected(effect_type: type["transition"], selected_effect:"transition", /, set_by_hotkey:bool=False) -> None:
    global recent_effects

    if effect_type in recent_effects and not set_by_hotkey:
        selected_effect._set_observer(recent_effects[effect_type].get_observer())
        #the above line uses merge so it only copies value and not reference:
        recent_effects[effect_type].set_observer(selected_effect.get_observer())
        return
    
    ##recent_effects handling
    if not set_by_hotkey:
        for recent_effect_type, recent_effect in recent_effects.items():
            if effect_type == recent_effect_type:
                selected_effect._set_observer(recent_effect.get_observer())
                break

    recent_effects[effect_type] = Recent_observer(selected_effect.get_observer(), selected_effect.get_name())
    
    return

def effect_was_sent(
    selected_effect: "transition",
    effect_type: type["transition"],
    set_configurating_effect_func: Callable[..., "transition"],
) -> None:
    global recent_effects, hotkey_effects
    recent_effects[effect_type] = Recent_observer(selected_effect.get_observer(), selected_effect.get_name())

    for key, value in hotkey_effects.items():
        hotkey:"Hotkey" = value["hotkey"]
        if hotkey is None:
            continue
        #we do a manual comparison instead of creating a hotkey and comparing bcs it will mess up the hotkey's key order
        if hotkey.get_unitialized_effect() == effect_type and hotkey.get_observer().is_equal(selected_effect.get_observer()):
            break
    else:
        keys.general_observer.subscribe(Hotkey(set_configurating_effect_func, effect_type, selected_effect.get_observer().clone(), selected_effect.get_name()))
    

def get_recent_and_hotkey_effects() -> tuple[dict[type["transition"], Recent_observer], dict[str, dict[str, Hotkey|PreviewEngine]]]:
    return recent_effects, hotkey_effects

def get_to_delete_hotkey_index() -> int:
    return next_hotkey_index

