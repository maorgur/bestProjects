import keys
import brain
import tools
import random
from config import N_PIXELS, HALF_PIXELS

def subscribe_effect(effect:brain.transition, key:str):
    keys.general_observer.subscribe(keys.effectKeybind(key, lambda: brain.set_configurating_effect(effect)))

class blankEffect(brain.transition):
    def __init__(self):
        super().__init__("Blank")
    
    def get_frame(self, previous_frame, current_frame):
        return [[0,0,0]]*N_PIXELS
subscribe_effect(blankEffect, "blank")

class solidEffect(brain.transition):
    def __init__(self):
        super().__init__("Solid")
        self.color = None

    def start(self):
        self.color = keys.get_main_color()
    
    def get_frame(self, previous_frame, current_frame):
        return [self.color]*N_PIXELS
subscribe_effect(solidEffect, "solid")

class start(brain.transition):
    def __init__(self):
        self.end_frame = None
        super().__init__("Start", beats_duration=2)
        self.set_base(False) #must be after super init bcs the object hasen't fully made yet before

    def start(self):
        self.end_frame = [keys.get_main_color()]*N_PIXELS
        
        super().start()

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        return tools.fade_frames(current_frame, self.end_frame, progress)
    
    def finished_lap(self):
        self.set_base(True)
        self.end()
        return super().finished_lap()
    
subscribe_effect(start, "start")

class end(brain.transition):
    def __init__(self):
        super().__init__("End", beats_duration=2)
        self.set_base(False)

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        return tools.fade_frames(current_frame, [[0,0,0]]*N_PIXELS, progress)
    
    def finished_lap(self):
        self.end()
        self.set_base(True)
        return super().finished_lap()
subscribe_effect(end, "end")

class pulse(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.blackouts_or_between_colors_m = self.observer.subscribe(keys.Modifier("Colors", ["Through black", "Through secondary"]))
        self.random_m = self.observer.subscribe(keys.Modifier("Random"))
        self.single_m = self.observer.subscribe(keys.Modifier("Single pixel"))

        self.wave_width_s = self.observer.subscribe(keys.Slider("Wave width", 0.1, 1,step=0.1, default_value=1))

        self.observer.subscribe(keys.Preset("Default", slider_values={self.wave_width_s: 1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through black", self.random_m: False, self.single_m: False}))
        self.observer.subscribe(keys.Preset("Color", slider_values={self.wave_width_s: 1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through secondary", self.random_m: False, self.single_m: False}))
        self.observer.subscribe(keys.Preset("Background", slider_values={self.wave_width_s: 1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through black", self.random_m: True, self.single_m: False}))
        self.observer.subscribe(keys.Preset("Background color", slider_values={self.wave_width_s: 1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through secondary", self.random_m: True, self.single_m: False}))
        self.observer.subscribe(keys.Preset("Twinkle", slider_values={self.wave_width_s: 0.1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through black", self.random_m: True, self.single_m: False}))
        self.observer.subscribe(keys.Preset("Single", slider_values={self.wave_width_s: 1}, modifier_values={
            self.blackouts_or_between_colors_m: "Through secondary", self.random_m: False, self.single_m: True}))
        
        super().__init__("Pulse", observer=self.observer)
    
    def generate_ordering(self):
        self.ordering = [x/N_PIXELS for x in list(range(N_PIXELS))]
        random.shuffle(self.ordering)

    def start(self):

        self.color1 = keys.get_main_color()
        self.color2 = keys.get_secondary_color() if self.blackouts_or_between_colors_m.get_value() == "Through secondary" else [0,0,0]  

        self.frame1 = [self.color1]*N_PIXELS
        self.frame2 = [self.color2]*N_PIXELS

        self.generate_ordering()

        self.single_pixel_index = random.randint(0, N_PIXELS-1)

        self.set_base(not self.single_m.is_active()) #if one pixel, then it's an overlay

        self.progress_multiplier = (1/self.wave_width_s.get_value())
        if self.random_m.is_active() and not self.single_m.is_active():
            self.progress_multiplier *= 2

        super().start(self.progress_multiplier)

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        if not self.single_m.is_active():
            if not self.random_m.is_active():
                
                pulsing_progress = tools.symmetric_crop_progress(tools.pulsing_progress(progress), self.wave_width_s.get_value())
                result = tools.fade_frames(self.frame2, self.frame1, pulsing_progress)
            else:
                for pixel in range(N_PIXELS):
                    current_frame[pixel] = tools.fade_color(self.color2, self.color1, tools.symmetric_crop_progress(tools.circular_distance(self.ordering[pixel], progress), self.wave_width_s.get_value())*2)
                result = current_frame
            
            return tools.fade_from_previous_frame(previous_frame, result, self.get_absolute_progress(), self.progress_multiplier)
            
        else: #random and both colors modifiers are ignored, irrelevent
            progress = tools.pulsing_progress(progress)
            current_frame[self.single_pixel_index] = tools.fade_color([0,0,0], self.color1, progress)
            return current_frame
    
    def finished_lap(self):
        if self.single_m.is_active():
            self.end()
        super().finished_lap()

subscribe_effect(pulse, "pulse")

class strobe(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()

        self.second_color_m = self.observer.subscribe(keys.Modifier("Second color"))
        self.blackouts_m = self.observer.subscribe(keys.Modifier("Blackouts", default_option=1))
        self.intensity_s = self.observer.subscribe(keys.Slider("Intensity", 0.1, 1, step=0.1, default_value=0.5))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.second_color_m: False, self.blackouts_m: True}, slider_values={self.intensity_s: 0.5}))
        self.observer.subscribe(keys.Preset("Smooth ", modifier_values={self.second_color_m: False, self.blackouts_m: False}, slider_values={self.intensity_s: 0.5}))

        self.observer.subscribe(keys.Preset("2 colors", modifier_values={self.second_color_m: True, self.blackouts_m: True}, slider_values={self.intensity_s: 0.5}))
        self.observer.subscribe(keys.Preset("2 colors smooth", modifier_values={self.second_color_m: True, self.blackouts_m: False}, slider_values={self.intensity_s: 0.5}))

        self.observer.subscribe(keys.Preset("Together", modifier_values={self.second_color_m: False, self.blackouts_m: True}, slider_values={self.intensity_s: 1}))
        self.observer.subscribe(keys.Preset("2 colors together", modifier_values={self.second_color_m: True, self.blackouts_m: True}, slider_values={self.intensity_s: 1}))

        self.observer.subscribe(keys.Preset("Twinkle", modifier_values={self.second_color_m: False, self.blackouts_m: False}, slider_values={self.intensity_s: 0.1}))

        super().__init__("Strobe", observer=self.observer)

    def create_random_frame(self, main_color, secondary_color) -> list[list[int]]:
        random_intensity = self.intensity_s.get_value()
        if random_intensity >= 1:
            return [main_color]*N_PIXELS
        return [main_color if random.random() <= random_intensity else secondary_color for _ in range(N_PIXELS)]

    def start(self):
        self.color1 = keys.get_main_color()
        self.color2 = keys.get_secondary_color() if self.second_color_m.is_active() else [0,0,0]

        self.random_frame = self.create_random_frame(self.color1, self.color2)
        self.generated_random_frame = True

        super().start(beats_duration=0.5 if not self.blackouts_m.is_active() else None)

    def get_frame(self, previous_frame, current_frame):
        if self.get_progress() % 0.2 > 0.1:
            if not self.generated_random_frame:
                self.random_frame = self.create_random_frame(self.color1, self.color2)
                self.generated_random_frame = True
            return self.random_frame
        else:
            self.generated_random_frame = False
            if self.blackouts_m.is_active():
                if self.second_color_m.is_active():
                    return [self.color2]*N_PIXELS
                else:
                    return [[0,0,0]]*N_PIXELS
            else:
                return self.random_frame
subscribe_effect(strobe, "strobe")

class snap(brain.transition):
    def __init__(self):

        self.observer = keys.KeybindObserver()
        self.to_black_or_secondary_m = self.observer.subscribe(keys.Modifier("To color", ["Black", "Secondary"]))
        self.snap_off_m = self.observer.subscribe(keys.Modifier("Snap off"))
        self.random_pixels_m = self.observer.subscribe(keys.Modifier("Random"))
        self.single_pixel_m = self.observer.subscribe(keys.Modifier("Single pixel"))

        self.random_intensity_s = self.observer.subscribe(keys.Slider("Random intensity", 0.1, 1, step=0.1, default_value=1))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.to_black_or_secondary_m: "Black", self.snap_off_m: False, 
                                self.random_pixels_m: False, self.single_pixel_m: False}, slider_values={self.random_intensity_s: 1}))
        self.observer.subscribe(keys.Preset("To secondary", modifier_values={self.to_black_or_secondary_m: "Secondary", self.snap_off_m: False, 
                                self.random_pixels_m: False, self.single_pixel_m: False}, slider_values={self.random_intensity_s: 1}))
        self.observer.subscribe(keys.Preset("Random", modifier_values={self.to_black_or_secondary_m: "Black", self.snap_off_m: False, 
                                self.random_pixels_m: True, self.single_pixel_m: False}, slider_values={self.random_intensity_s: 1}))
        self.observer.subscribe(keys.Preset("Twinkle", modifier_values={self.to_black_or_secondary_m: "Black", self.snap_off_m: False, 
                                self.random_pixels_m: True, self.single_pixel_m: False}, slider_values={self.random_intensity_s: 0.1}))
        self.observer.subscribe(keys.Preset("Single pixel", modifier_values={self.to_black_or_secondary_m: "Black", self.snap_off_m: False, 
                                self.random_pixels_m: False, self.single_pixel_m: True}, slider_values={self.random_intensity_s: 1}))
        self.observer.subscribe(keys.Preset("Snap off", modifier_values={self.to_black_or_secondary_m: "Black", self.snap_off_m: True, 
                                self.random_pixels_m: False, self.single_pixel_m: False}, slider_values={self.random_intensity_s: 1}))
        
        super().__init__("Snap", observer=self.observer)

    def generate_ordering(self):
        self.ordering = [x/N_PIXELS for x in list(range(N_PIXELS))]
        random.shuffle(self.ordering)

    def start(self):
        self.color1 = keys.get_main_color()
        self.color2 = keys.get_secondary_color() if self.to_black_or_secondary_m.get_value() == "Secondary" else [0,0,0]

        self.frame1 = [self.color1]*N_PIXELS
        self.frame2 = [self.color2]*N_PIXELS

        self.random_pixel = random.randint(0, N_PIXELS-1)

        self.generate_ordering()

        self.set_base(not self.single_pixel_m.is_active()) #overlay, only one pixel changes, so we want the previous frame to be the base

        self.progress_multiplier = 1/self.random_intensity_s.get_value()
        if not self.random_pixels_m.is_active() or self.single_pixel_m.is_active():
            self.progress_multiplier = 1

        super().start(beats_duration=self.progress_multiplier)
    
    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        if self.snap_off_m.is_active():
            progress = 1 - progress
        if not self.single_pixel_m.is_active():
            if not self.random_pixels_m.is_active():
                return tools.fade_frames(self.frame1, self.frame2, progress)
            else:
                for pixel in range(N_PIXELS):
                    current_frame[pixel] = tools.fade_color(self.color1, self.color2, tools.crop_progress(tools.circular_distance(self.ordering[pixel], progress, b_is_right_to_a=True), 0, self.random_intensity_s.get_value()))
                return tools.fade_from_previous_frame(previous_frame, current_frame, self.get_absolute_progress(), self.progress_multiplier)
        else:
            current_frame[self.random_pixel] = tools.fade_color(self.color1, current_frame[self.random_pixel], progress)
            return current_frame
        
    def finished_lap(self):
        if self.single_pixel_m.is_active():
            self.end()
        super().finished_lap()
subscribe_effect(snap, "snap")

class sides(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.switch_places_m = self.observer.subscribe(keys.Modifier("Switch places"))
        self.fade_mode_m = self.observer.subscribe(keys.Modifier("Fade mode", ["Static", "Pulse", "Snap on"]))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.switch_places_m: False, self.fade_mode_m: "Static"}))
        self.observer.subscribe(keys.Preset("Switcher", modifier_values={self.switch_places_m: True, self.fade_mode_m: "Static"}))

        self.observer.subscribe(keys.Preset("Pulse", modifier_values={self.switch_places_m: False, self.fade_mode_m: "Pulse"}))
        self.observer.subscribe(keys.Preset("Snap on", modifier_values={self.switch_places_m: False, self.fade_mode_m: "Snap on"}))

        self.observer.subscribe(keys.Preset("Color pulse", modifier_values={self.switch_places_m: True, self.fade_mode_m: "Pulse"}))



        super().__init__("Sides", observer=self.observer, beats_duration=2)

    def start(self):
        self.color1 = keys.get_main_color()
        self.weak_color1 = tools.fade_color([0,0,0], self.color1, 0.05)
        self.color2 = keys.get_secondary_color()
        self.weak_color2 = tools.fade_color([0,0,0], self.color2, 0.05)

        if not self.switch_places_m.is_active():
            self.frame_1 = [self.color1 if pixel < HALF_PIXELS else self.weak_color2 for pixel in range(N_PIXELS)]
            self.frame_2 = [self.weak_color1 if pixel < HALF_PIXELS else self.color2 for pixel in range(N_PIXELS)]
        else:
            self.frame_1 = [self.color1 if pixel < HALF_PIXELS else self.color2 for pixel in range(N_PIXELS)]
            self.frame_2 = [self.color2 if pixel < HALF_PIXELS else self.color1 for pixel in range(N_PIXELS)]

        super().start()

    
    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        if self.fade_mode_m.get_value() == "Static":
            if progress < 0.5:
                return self.frame_1
            else:
                return self.frame_2
        elif self.fade_mode_m.get_value() == "Pulse":
            new_frame = [[]]*N_PIXELS
            if not self.switch_places_m.is_active():
                new_frame[:HALF_PIXELS] = [tools.fade_color(self.weak_color1, self.color1, tools.circular_distance(0, progress)*2)]*HALF_PIXELS
                new_frame[HALF_PIXELS:] = [tools.fade_color(self.weak_color2, self.color2, tools.circular_distance(0.5, progress)*2)]*HALF_PIXELS
            else:
                new_frame[:HALF_PIXELS] = [tools.fade_color(self.color1, self.color2, tools.circular_distance(0, progress)*2)]*HALF_PIXELS
                new_frame[HALF_PIXELS:] = [tools.fade_color(self.color2, self.color1, tools.circular_distance(0, progress)*2)]*HALF_PIXELS
            new_frame = tools.fade_from_previous_frame(previous_frame, new_frame, self.get_absolute_progress())
            return new_frame
        elif self.fade_mode_m.get_value() == "Snap on":
            new_frame = [[]]*N_PIXELS
            if not self.switch_places_m.is_active():
                new_frame[:HALF_PIXELS] = [tools.fade_color(self.weak_color1, self.color1, tools.circular_distance(progress, 0, b_is_right_to_a=True))]*HALF_PIXELS
                new_frame[HALF_PIXELS:] = [tools.fade_color(self.weak_color2, self.color2, tools.circular_distance(progress, 0.5, b_is_right_to_a=True))]*HALF_PIXELS
            else:
                new_frame[:HALF_PIXELS] = [tools.fade_color(self.color1, self.color2, tools.circular_distance(0, progress, b_is_right_to_a=True))]*HALF_PIXELS
                new_frame[HALF_PIXELS:] = [tools.fade_color(self.color1, self.color2, tools.circular_distance(0.5, progress, b_is_right_to_a=True))]*HALF_PIXELS
            #no fade_from_last_frame cuz it should be snappy
            return new_frame
        
subscribe_effect(sides, "sides")
    
class flash(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.white_m = self.observer.subscribe(keys.Modifier("White"))
        self.to_black_or_secondary_m = self.observer.subscribe(keys.Modifier("To color", ["Off", "Black", "Main"]))
        self.width_s = self.observer.subscribe(keys.Slider("Width", 0.1, 1, step=0.1, default_value=1))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.white_m: False, self.to_black_or_secondary_m:"Off"}, slider_values={self.width_s: 1}))
        self.observer.subscribe(keys.Preset("White", modifier_values={self.white_m: True, self.to_black_or_secondary_m:"Off"},slider_values={self.width_s: 1}))

        self.observer.subscribe(keys.Preset("To black", modifier_values={self.white_m: False, self.to_black_or_secondary_m: "Black"}, slider_values={self.width_s: 1}))
        self.observer.subscribe(keys.Preset("To primary", modifier_values={self.white_m: False, self.to_black_or_secondary_m: "Main"}, slider_values={self.width_s: 1}))

        self.observer.subscribe(keys.Preset("Middle", modifier_values={self.white_m: False, self.to_black_or_secondary_m:"Off"}, slider_values={self.width_s: 0.3}))
        self.observer.subscribe(keys.Preset("Middle white", modifier_values={self.white_m: True, self.to_black_or_secondary_m:"Off"}, slider_values={self.width_s: 0.3}))

        super().__init__("Flash", observer=self.observer)
        self.set_base(False)


    def start(self):
        self.main_color = keys.get_main_color()
        self.secondary_color = keys.get_secondary_color() if not self.white_m.is_active() else [255,255,255]

        self.blob_width = (self.width_s.get_value()/(5/3)) * N_PIXELS
        self.border_width = min(self.blob_width, N_PIXELS/10)

        self.set_base(self.to_black_or_secondary_m.get_value() != "Off")

        super().start()

    def get_frame(self, previous_frame, current_frame):
        if self.to_black_or_secondary_m.get_value() == "Black":
            current_frame = [[0,0,0]]*N_PIXELS
        elif self.to_black_or_secondary_m.get_value() == "Main":
            current_frame = [self.main_color]*N_PIXELS

        return tools.blob_of_color(current_frame, self.secondary_color, HALF_PIXELS - self.blob_width, end_position=HALF_PIXELS + self.blob_width, border_width=self.border_width, fade=(1-self.get_progress()))
    
    def finished_lap(self):
        self.end()
        super().finished_lap()
subscribe_effect(flash, "flash")


class wave(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()

        self.direction_m = self.observer.subscribe(keys.Modifier("Direction", ["Left to right", "Bouncing", "Right to left"]))
        self.count_s = self.observer.subscribe(keys.Slider("Count", 1, round(N_PIXELS/10), step=1, default_value=1))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.direction_m: "Left to right"}, slider_values={self.count_s: 1}))
        self.observer.subscribe(keys.Preset("Bounce", modifier_values={self.direction_m: "Bouncing"}, slider_values={self.count_s: 1}))
        self.observer.subscribe(keys.Preset("RTL", modifier_values={self.direction_m: "Right to left"}, slider_values={self.count_s: 1}))

        self.observer.subscribe(keys.Preset("Half overlay", modifier_values={self.direction_m: "Left to right"}, slider_values={self.count_s: 2}))
        self.observer.subscribe(keys.Preset("Full overlay", modifier_values={self.direction_m: "Left to right"}, slider_values={self.count_s: 4}))

        self.observer.subscribe(keys.Preset("Bounce overlay", modifier_values={self.direction_m: "Bouncing"}, slider_values={self.count_s: 4}))
    
        super().__init__("Wave", observer=self.observer, beats_duration=4)
        self.set_base(False)

    def start(self):
        self.main_color = keys.get_main_color()
        self.secondary_color = keys.get_secondary_color()

        self.border_width = N_PIXELS/10
        super().start(beats_duration=4 if self.direction_m.get_value() != "Bouncing" else 8)

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        if self.direction_m.get_value() == "Right to left":
            progress = 1 - progress


        new_frame = current_frame
        is_main_color = True
        for index in range(self.count_s.get_value()):
            wave_index = (progress * N_PIXELS - self.border_width + index * (N_PIXELS/self.count_s.get_value()))

            #this logic makes sure that at the start the other circular side isnt colored
            if self.direction_m.get_value() == "Bouncing":
                is_circular = self.count_s.get_value() > 1
                #the modolu works good only if the border width is added before and removed later, but the bouncing has to be calculated with abs values so it's in the way
                wave_index = (wave_index + self.border_width) % N_PIXELS

                if wave_index < HALF_PIXELS:
                    wave_index *= 2
                else:
                    wave_index = (N_PIXELS - wave_index) *2

                wave_index -= self.border_width
                
            else:
                is_circular = self.get_absolute_progress() * N_PIXELS > self.border_width or index > 0

            new_frame = tools.blob_of_color(new_frame, self.main_color if is_main_color else self.secondary_color, wave_index, pixels_count=0, border_width=self.border_width, circular=is_circular)
            is_main_color = not is_main_color
            
        return tools.fade_from_previous_frame(current_frame, new_frame, self.get_absolute_progress(), 4 if self.direction_m.get_value() != "Bouncing" else 8)
subscribe_effect(wave, "wave")

class rainbow(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()

        self.jumps_m = self.observer.subscribe(keys.Modifier("Jumps"))
        self.uniform_m = self.observer.subscribe(keys.Modifier("Uniform"))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.uniform_m: False, self.jumps_m: False}))
        self.observer.subscribe(keys.Preset("Jumps", modifier_values={self.uniform_m: True, self.jumps_m: True}))
        self.observer.subscribe(keys.Preset("Uniform", modifier_values={self.uniform_m: True, self.jumps_m: False}))

        super().__init__("Rainbow", self.observer, beats_duration=8)

    
    def get_frame(self, previous_frame, current_frame):
        progress = 1 - self.get_progress() #reversed looks more correct
        if self.jumps_m.is_active():
            progress = int(progress * 8)/8
    
        new_frame = [[]]*N_PIXELS
        if not self.uniform_m.is_active():
            for pixel in range(N_PIXELS):
                hue = (pixel/N_PIXELS + progress) % 1
                new_frame[pixel] = tools.HSV_to_RGB(hue*360, 1, 1)
        else:
            color = tools.HSV_to_RGB(progress*360, 1, 1)
            new_frame = [color]*N_PIXELS

        return tools.fade_from_previous_frame(previous_frame, new_frame, self.get_absolute_progress(), 8)
subscribe_effect(rainbow, "rainbow")

class pixel_chase(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.directon_m = self.observer.subscribe(keys.Modifier("Direction", ["Outwards", "Inwards"]))
        self.gaps_m = self.observer.subscribe(keys.Modifier("Segments", ["Smooth", "Tied", "Jumps"]))

        self.width_s = self.observer.subscribe(keys.Slider("Segment width", 0, 10, step=1, default_value=2))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.directon_m: "Outwards", self.gaps_m: "Smooth"}, slider_values={self.width_s: 2}))
        self.observer.subscribe(keys.Preset("Default Inwards", modifier_values={self.directon_m: "Inwards", self.gaps_m: "Smooth"}, slider_values={self.width_s: 2}))

        self.observer.subscribe(keys.Preset("Tied", modifier_values={self.directon_m: "Outwards", self.gaps_m: "Tied"}, slider_values={self.width_s: 2}))
        self.observer.subscribe(keys.Preset("Tied Inwards", modifier_values={self.directon_m: "Inwards", self.gaps_m: "Tied"}, slider_values={self.width_s: 2}))

        self.observer.subscribe(keys.Preset("Segmented", modifier_values={self.directon_m: "Outwards", self.gaps_m: "Jumps"}, slider_values={self.width_s: 2}))
        self.observer.subscribe(keys.Preset("Segmented Inwards", modifier_values={self.directon_m: "Inwards", self.gaps_m: "Jumps"}, slider_values={self.width_s: 2}))

        self.observer.subscribe(keys.Preset("Spaced", modifier_values={self.directon_m: "Outwards", self.gaps_m: "Tied"}, slider_values={self.width_s: 8}))
        self.observer.subscribe(keys.Preset("Spaced Inwards", modifier_values={self.directon_m: "Inwards", self.gaps_m: "Tied"}, slider_values={self.width_s: 8}))

        self.observer.subscribe(keys.Preset("Condensed", modifier_values={self.directon_m: "Outwards", self.gaps_m: "Jumps"}, slider_values={self.width_s: 0}))


        super().__init__("Pixel chase", self.observer, beats_duration=2)

    def start(self):
        self.main_color = keys.get_main_color()
        self.secondary_color = keys.get_secondary_color()
        
        self.segment_length = int(self.width_s.get_value() * (N_PIXELS/20)) #20 and not ten bcs there is no reason to go more than that
        if self.segment_length == 0:
            self.segment_length = 1

        elif self.segment_length % 2 == 1: #it gets weird when its odd with the a blob with harsh edges
            self.segment_length += 1
        
        self.effect_length = self.width_s.get_value()
        if self.effect_length == 0: self.effect_length = 1
        if self.gaps_m.get_value() == "jumps": self.effect_length /=2
        super().start(self.effect_length)

    def get_frame(self, previous_frame, current_frame):
        duration = self.get_progress()
        if (self.directon_m.get_value() == "Inwards") != (self.gaps_m.get_value() == "Jumps"): #XOR gate (jumps works in reverse, so this will fix it)
            duration = 1 - duration

        frame = [[0,0,0]] * N_PIXELS
        
        current_color = False

        if self.gaps_m.get_value() != "Jumps":
            offset = duration * self.segment_length*4
            pixel = HALF_PIXELS - offset + self.segment_length*4
            while pixel >= -self.segment_length:
                frame[:HALF_PIXELS] = tools.blob_of_color(frame[:HALF_PIXELS], self.main_color if current_color else self.secondary_color, pixel, self.segment_length) #<--
                current_color = not current_color
                if self.gaps_m.get_value() != "Tied":
                    pixel -= self.segment_length*2
                else:
                    pixel -= self.segment_length

        else:
            if duration > 0.5:
                duration -= 0.5
                current_color = True
            else:
                current_color = False
            duration *= 2

            
            current_segment_index = -int(duration * 3) #1: 3 cuz 2 will look like its alternating. 2: if its positive then the current_color IS A MESS
            
            current_pixel = 0
            while current_pixel < HALF_PIXELS:
                if current_segment_index % 3 == 0:
                    frame = tools.blob_of_color(frame, self.main_color if current_color else self.secondary_color, current_pixel, self.segment_length)
                    current_color = not current_color

                current_pixel += self.segment_length
                current_segment_index += 1

        frame[HALF_PIXELS:] = frame[:HALF_PIXELS][::-1]

        return tools.fade_from_previous_frame(previous_frame, frame, self.get_absolute_progress(), self.effect_length)
subscribe_effect(pixel_chase, "pixel chase")

class fade_chase(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.directon_m = self.observer.subscribe(keys.Modifier("Direction", ["Outwards", "Inwards"]))

        self.width_s = self.observer.subscribe(keys.Slider("Segment width", 1, 10, step=1, default_value=1))
        self.intensity_s = self.observer.subscribe(keys.Slider("Intensity", 0.1, 1, step=0.1, default_value=0.5))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.directon_m: "Outwards"}, slider_values={self.width_s: 1, self.intensity_s: 0.5}))
        self.observer.subscribe(keys.Preset("Default inwards", modifier_values={self.directon_m: "Inwards"}, slider_values={self.width_s: 1, self.intensity_s: 0.5}))

        self.observer.subscribe(keys.Preset("Spaced", modifier_values={self.directon_m: "Outwards"}, slider_values={self.width_s: 5, self.intensity_s: 0.7}))
        self.observer.subscribe(keys.Preset("Spaced inwards", modifier_values={self.directon_m: "Inwards"}, slider_values={self.width_s: 5, self.intensity_s: 0.7}))

        self.observer.subscribe(keys.Preset("Half", modifier_values={self.directon_m: "Outwards"}, slider_values={self.width_s: 2, self.intensity_s: 0.3}))
        self.observer.subscribe(keys.Preset("Half inwards", modifier_values={self.directon_m: "Inwards"}, slider_values={self.width_s: 2, self.intensity_s: 0.3}))

        super().__init__("Fade chase", self.observer)

    def start(self):
        self.main_color = keys.get_main_color()
        self.secondary_color = keys.get_secondary_color()
        
        #NOTE: there is a flickering issue, couldn't fix it but it's subtle and only if width is low
        self.segment_length = int(tools.map_value(self.width_s.get_value(), 1, 10, N_PIXELS/10, N_PIXELS/2))
        

        if self.directon_m.get_value() == "Outwards":
            self.border_width = [0, self.segment_length*self.intensity_s.get_value()*2]
        else:
            self.border_width = [self.segment_length*self.intensity_s.get_value()*2, 0]


        self.effect_length = tools.map_value(self.width_s.get_value(), 1, 10, 2, 8)
        super().start(self.effect_length)

    def get_frame(self, previous_frame, current_frame):
        duration = self.get_progress()
        if self.directon_m.get_value() == "Inwards":
            duration = 1 - duration

        frame = [[0,0,0]] * int(N_PIXELS/2)
        
        current_color = False

        if self.directon_m.get_value() == "Inwards":
            offset = duration * self.segment_length*4
            pixel = HALF_PIXELS - offset + self.segment_length*4
            while pixel >= -self.segment_length*2:
                frame = tools.blob_of_color(frame, self.main_color if current_color else self.secondary_color, pixel, pixels_count = 0, border_width=self.border_width, blend_with_other_colors=False) #<--
                current_color = not current_color
                pixel -= self.segment_length
        else:
            offset = duration * self.segment_length*4
            pixel = -offset
            while pixel < HALF_PIXELS + self.segment_length*4:
                frame = tools.blob_of_color(frame, self.main_color if current_color else self.secondary_color, pixel, pixels_count = 0, border_width=self.border_width, blend_with_other_colors=False) #<--
                current_color = not current_color
                pixel += self.segment_length

        frame += frame[:HALF_PIXELS][::-1]

        return tools.fade_from_previous_frame(previous_frame, frame, self.get_absolute_progress(), self.effect_length)
subscribe_effect(fade_chase, "fade chase")

class zoom(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.direction_m = self.observer.subscribe(keys.Modifier("Direction", ["From center", "From sides"]))
        self.temporary_m = self.observer.subscribe(keys.Modifier("Temporary"))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.direction_m: "From center", self.temporary_m: False}))
        self.observer.subscribe(keys.Preset("From sides", modifier_values={self.direction_m: "From sides", self.temporary_m: False}))

        self.observer.subscribe(keys.Preset("Temporary", modifier_values={self.direction_m: "From center", self.temporary_m: True}))
        self.observer.subscribe(keys.Preset("Temporary from sides", modifier_values={self.direction_m: "From sides", self.temporary_m: True}))
        
        super().__init__("Zoom", self.observer, beats_duration=4)

    def start(self):
        self.color = keys.get_main_color()
        self.border_width = N_PIXELS/5
        self.set_base(False)
        super().start()

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        
        if self.direction_m.get_value() == "From center":
            offset = progress * (HALF_PIXELS + self.border_width)
            start = HALF_PIXELS - offset
            end = HALF_PIXELS + offset
            frame = tools.blob_of_color(current_frame, self.color, start, end_position=end, border_width=min(self.border_width, offset))
        else:
            offset = progress * (HALF_PIXELS + self.border_width)
            left_pixel = offset
            right_pixel = N_PIXELS - offset
            frame = tools.blob_of_color(current_frame, self.color, 0, end_position=left_pixel, border_width=[0, min(self.border_width, offset)])
            frame = tools.blob_of_color(frame, self.color, right_pixel, end_position=N_PIXELS, border_width=[min(self.border_width, offset), 0])


        if progress > 0.8 and self.temporary_m.is_active(): #0.8 feels good number cuz its the same as the border width (1/5)
            frame = tools.fade_frames(frame, current_frame, tools.map_value(progress, 0.8, 1, 0, 1))

        return frame
        
    def finished_lap(self):
        if not self.temporary_m.is_active():
            self.set_base(True)
        self.end()
        super().finished_lap()
subscribe_effect(zoom, "zoom")

class alternate(brain.transition):
    def __init__(self):
        self.observer = keys.KeybindObserver()
        self.switching_places_m = self.observer.subscribe(keys.Modifier("Switch places"))
        self.through_black_m = self.observer.subscribe(keys.Modifier("Through black"))

        self.observer.subscribe(keys.Preset("Default", modifier_values={self.switching_places_m: False, self.through_black_m: False}))
        self.observer.subscribe(keys.Preset("Switching", modifier_values={self.switching_places_m: True, self.through_black_m: False}))
        self.observer.subscribe(keys.Preset("Harsh", modifier_values={self.switching_places_m: False, self.through_black_m: True}))
        self.observer.subscribe(keys.Preset("Harsh combined", modifier_values={self.switching_places_m: True, self.through_black_m: True}))

        super().__init__("Alternate", self.observer)

    def start(self):
        color1 = keys.get_main_color()
        color2 = keys.get_secondary_color()
        weak_color1 = tools.fade_color([0,0,0], color1, 0.05)
        weak_color2 = tools.fade_color([0,0,0], color2, 0.05)
        if not self.switching_places_m.is_active() and not self.through_black_m.is_active():
            self.frame1 = [weak_color1 if pixel%2 == 0 else color2 for pixel in range(N_PIXELS)]
            self.frame2 = [color1 if pixel%2 == 0 else weak_color2 for pixel in range(N_PIXELS)]

        if self.switching_places_m.is_active() and not self.through_black_m.is_active():
            self.frame1 = [color2 if pixel%2 == 0 else color1 for pixel in range(N_PIXELS)]
            self.frame2 = [color1 if pixel%2 == 0 else color2 for pixel in range(N_PIXELS)]

        if not self.switching_places_m.is_active() and self.through_black_m.is_active():
            self.frame1 = [weak_color1 if pixel%2 == 0 else color2 for pixel in range(N_PIXELS)]
            self.frame2 = [weak_color1 if pixel%2 == 0 else weak_color2 for pixel in range(N_PIXELS)]
            self.frame3 = [color1 if pixel%2 == 0 else weak_color2 for pixel in range(N_PIXELS)]
            self.frame4 = self.frame2

        if self.switching_places_m.is_active() and self.through_black_m.is_active():
            self.frame1 = [color2 if pixel%2 == 0 else color1 for pixel in range(N_PIXELS)]
            self.frame2 = [weak_color1 if pixel%2 == 0 else weak_color2 for pixel in range(N_PIXELS)]
            self.frame3 = [color1 if pixel%2 == 0 else color2 for pixel in range(N_PIXELS)]
            self.frame4 = [weak_color2 if pixel%2 == 0 else weak_color1 for pixel in range(N_PIXELS)]

        super().start()

    def get_frame(self, previous_frame, current_frame):
        progress = self.get_progress()
        if not self.through_black_m.is_active():
            progress = tools.pulsing_progress(progress)
            return tools.fade_from_previous_frame(previous_frame, tools.fade_frames(self.frame1, self.frame2, progress), self.get_absolute_progress())
        else:
            if progress < 0.25:
                return tools.fade_frames(self.frame1, self.frame2, tools.map_value(progress, 0, 0.25, 0, 1))
            elif progress < 0.5:
                return tools.fade_frames(self.frame2, self.frame3, tools.map_value(progress, 0.25, 0.5, 0, 1))
            elif progress < 0.75:
                return tools.fade_frames(self.frame3, self.frame4, tools.map_value(progress, 0.5, 0.75, 0, 1))
            else:
                return tools.fade_frames(self.frame4, self.frame1, tools.map_value(progress, 0.75, 1, 0, 1))
    
subscribe_effect(alternate, "alternate")
    


if __name__ == "__main__":
    keys.start_listening() #non-blocking code
    brain.update_constantly()