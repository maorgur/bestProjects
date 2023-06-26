import sys
if 'help' in sys.argv or '-h' in sys.argv:
    print('''\033[32;5m\033[38;2;0;0;255mwelcome to text convert!\033[0m

size - (number) how wide the text should be

color - add colors to text


\033[38;2;0;255;0mvideos\033[0m


you can open video to make a new video from text file

\033[32;5m\033[38;2;255;255;0mdownload ffmpeg for audio support\033[0m


''')
    quit()


print('\033[32;5m\033[38;2;255;255;0mloading libraries\033[0m', end = '\r')
try:
    from shutil import which
    import os
    from tkinter import Tk, filedialog
    import webbrowser
    from tqdm import tqdm
    import cv2
    from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont
    from numpy import array
    import os
except ImportError as e:
    e = str(e).split("'")[-2]
    if sys.platform == 'linux':
        print(f'\033[32;4m\033[38;2;255;255;0m{e}\033[32;24m\033[38;2;255;0;0m is not installed, install it using \033[32;4m\033[38;2;255;255;0mpip3 install {e}\033[0m')
    else:
        print(f'\033[32;4m\033[38;2;255;255;0m{e}\033[32;24m\033[38;2;255;0;0m is not installed, install it using \033[32;4m\033[38;2;255;255;0mpip install {e}\033[0m')
    quit()

if not which('ffmpeg'):
    if sys.platform == 'linux':
        print(f'\033[32;4m\033[38;2;255;255;0mffmpeg\033[32;24m\033[38;2;255;0;0m is not installed, video sound is disabled\033[32;4m\n\033[38;2;0;0;255minstall with:\033[0m \033[32;4m\033[38;2;0;255;0msudo apt install ffmpeg\033[0m')
    else:
        print(f'\033[32;4m\033[38;2;255;255;0mffmpeg\033[32;24m\033[38;2;255;0;0m is not installed, video sound is disabled\033[32;4m\n\033[38;2;0;0;255minstall link:\033[0m \033[32;4m\033[38;2;0;255;0mhttps://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip\033[0m (ZIP file)')
    ffmpeg = False
else: ffmpeg = True


dir_path = os.path.dirname(os.path.realpath(__file__))
dir_slash = '\\' if 'win' in sys.platform.lower() else '/'
frames_path = dir_path+dir_slash+'frames'

def load_font():
    global dir_path, dir_slash
    font = ImageFont.truetype(font=f"{dir_path}{dir_slash}mono text font.ttf", size=15)
    return font

try:
    font = load_font()
    font_mode = True
except:
    print('\033[38;2;255;0;0mfont file not found, make sure the file \033[32;4m\033[38;2;255;255;0mmono text font.ttf\033[0m\033[38;2;255;0;0m is in the same directory\n\033[38;2;0;255;0mdownload link: \033[32;4m\033[38;2;255;255;0mhttps://github.com/maorgur/external-files/raw/main/mono%20text%20font.ttf\033[0m\n\033[38;2;0;255;0mvideos will not be available, text images will not be available\033[0m')
    font_mode = False



video_width = None


for val in sys.argv:
    if val.startswith('size='):
        val = val[5:].lower()
        try:
            video_width = int(val)
            if video_width > 10000:
                print(f'\033[38;2;255;0;0mmaximum size is 10,000\033[0m        ')
                quit()

            print(f'\033[38;2;0;0;255msize set to {video_width}\033[0m        ')
        except ValueError:
            print('\033[32;5m\033[38;2;255;0;0msize must be an absolute number\033[0m')
            quit()
        del val

if video_width == None:
        video_width = 80
        print('\033[38;2;0;0;255msize set to default (80), to change it, add size=number\033[0m')

if 'color' in sys.argv:
    color_mode = True
    print('\033[38;2;0;255;0mcolor mode is active\033[0m')
else:
    print('\033[38;2;255;0;0mcolor mode is \033[32;4m\033[38;2;255;0;0mnot\033[32;24m\033[38;2;255;0;0m active, activate it by adding \'color\'\033[0m')
    color_mode = False

def get_path(video = True):
    '''returns the path selected by the user using filedialog'''
    if video: 
        options = [("CLICK TO CHANGE video files", "*.avi *.mp4 *.mov")]
    else:
        options = []
    
    options.append(("CLICK TO CHANGE picture files", "*.jpg *.png *.jpeg *.bmp"))

    options.append(('CLICK TO CHANGE all files', '*.*')) 
    try:
        
        root = Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(title="Select video file",filetypes=options)
        root.destroy()
        return filename
    except KeyboardInterrupt:
        print('\033[38;2;255;0;0mCtrl+C pressed\033[0m')
        quit()

def load_video(path, video_width, max_pixels = 178956970):
    '''returns the frames of the video as a list'''
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    pixels_size_check = False
    frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"\033[38;2;0;255;0mfps: {int(fps)}    total frames: {frames_count}    length: {int(frames_count//fps)} seconds\033[0m")
    frames = []
    for frame_index in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))), 'loading video, \033[32;4m\033[38;2;255;0;0mdo not modify the video file\033[0m', colour = '#ff0000', leave = False):
        frame_index, frame = cap.read()
        frame = convert_cv2_to_pil(frame)
        if pixels_size_check == False:
            pixels_size_check = True
            pixels_size = convert_pixels_to_text(fit_size(frame, video_width), fit_size(frame, video_width).size, check_size=True)
            if pixels_size > max_pixels:
                if video_width == 80:
                    video_width = int(video_width/(pixels_size/max_pixels)-1)
                else:
                    print(f'\n\033[38;2;255;0;0msize is too large for this video, \033[32;4m\033[38;2;255;255;0m{int(video_width/(pixels_size/max_pixels)-1)}\033[0m\033[38;2;255;255;0m is the highest size for this video')
                    quit()

        frame = fit_size(frame, video_width)
        frames.append(frame)
    #check the fps of video
    cap.release()
    return [frames, fps, int(len(frames)/fps)]

def fit_size(image, size = 500):
    '''returns the image to fit the screen'''
    if image.width > size:
        image = image.resize((size, int(image.height * (size / image.width))))
    return image

def convert_cv2_to_pil(frame):
    '''converts a cv2 frame to a PIL image'''
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(frame)
    frame = Image.new('RGBA', img.size, 'white')
    try:
        frame.paste(img, (0, 0), img)
    except ValueError:
        frame = img
    #frame = frame.convert('L')
    if isinstance(video_width, int):
        frame = fit_size(frame).resize((int(frame.width * (video_width / frame.height)), video_width))
    return frame

def convert_pil_to_cv2(image):
    '''converts a PIL image to a cv2 frame'''
    image = image.convert('RGB')
    frame = array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
    return frame

def create_video(frames_folder_path, fps, filename, load_desc = None, leave = False):
    global dir_slash
    img = Image.open(frames_folder_path + dir_slash+ 'frame0000000.jpg')
    out = cv2.VideoWriter(f'{filename}.avi',cv2.VideoWriter_fourcc(*'XVID'), fps, img.size)
    #for image in tqdm(os.listdir(frames_folder_path), load_desc , colour = '#ff9500', leave=leave):
    for image in tqdm(os.listdir(frames_folder_path), load_desc , colour = '#ff9500', leave=leave):
        if image.endswith(".jpg"):
            out.write(convert_pil_to_cv2(Image.open(frames_folder_path + '/' + image)))
    out.release()

def get_values():
    '''returns values of letters'''
    global font_mode
    if not font_mode: #values for CascadiaCode
        return {'`': 4, '1': 16, '2': 21, '3': 15, '4': 22, '6': 24, '7': 20, '0': 26, '-': 7, '=': 14, '~': 10, '!': 8, '@': 29, '$': 30, '&': 25, '+': 13, 'e': 19, 't': 18, 'u': 17, 'W': 27, 'h': 12, 'A': 23, 'D': 28, ',': 5, '.': 2, 'B': 33, ' ': 0}, 33
    chars = '`1234567890-=~!@#$%^&*()_+qwqertyuiop[]|QWERTYUIOP{}|asdfghjkl;ASDFGHJKL:"zxcvbnm,./ZXCVBNM<>? '
    values = {}
    max_color = 0
    for char in chars:
        white_img = Image.new('RGB', (100, 100), color = 'black')
        count = 0
        pixels_img = write_Text(white_img, char, 60, force_font=True)
        pixels = pixels_img.load()
        for x in range(100):
            for y in range(100):
                if pixels[x,y][0] > 200:
                    count +=1
        if not count in list(values.values()):
            values[char] = count
        if count > max_color:
            max_color = count
    return values, max_color

def write_Text(image, text, size = 15, force_font = False):
    global font
    '''writes the text to the image'''
    if force_font:
        font = load_font()


    draw = ImageDraw.Draw(image)
    #font = ImageFont.load_default()
    draw.text((0, 0), text, font=font, fill='white', align='center')
    if force_font:
        font = load_font()

    return image

def add_colors(old_img, text_img, backround = (0, 0, 0), progress = False):
    old_img = old_img.resize(text_img.size)
    old_img_p = old_img.load()
    text_img_p = text_img.load()
    
    if not progress:
        for x in range(old_img.size[0]):
            for y in range(old_img.size[1]):
                if text_img_p[x, y] != backround:
                    text_img_p[x, y] = old_img_p[x, y]
    
    else: 
        for x in tqdm(range(old_img.size[0]), 'adding colors', colour='#ff0000'):
            for y in range(old_img.size[1]):
                if text_img_p[x, y] != backround:
                    text_img_p[x, y] = old_img_p[x, y]

    return text_img
    
def convert_pixels_to_text(frame, size, return_text = False, longest = None, end = None, return_len_end = False, once = False, color_mode_f = False, only_text = False, check_size = False):
    global val_based, next_img

    output = ''
    frame = frame.convert('RGBA')
    p_frame = frame.convert('L').load()

    if check_size:
        return size[1]*20*size[0]*2*9+5+9

        

    output += '\n'
    for y in range(size[1]):
        for x in range(size[0]):
            #get the color of the pixel
            output += val_based[p_frame[x, y]] * 2
        output += '\n'

    if only_text:
        return output
    

    if not once:
        if next_img[0] == output:
            if return_text:
                return [output, next_img[1]]
            else:
                return next_img[1]

    if return_len_end or longest == None:
        longest = 0
        for x in output.splitlines()[:-1]:
            if len(x) > longest:
                longest = len(x)


        longest = longest * 9 + 5
        end = len(output.splitlines()) * 20 + 5
        if return_len_end:
            return longest, end
    text_img = Image.new('RGB', ((longest, end)), )
    text_img = write_Text(text_img, output)
    if color_mode_f:
        text_img = add_colors(frame, text_img)
    next_img = [output, text_img]
    if return_text:
        return [output, text_img]
    else:
        return text_img
    
def copy_sound_from_video(video_filename, mode = 'copy', new_name = None):
    global dir_path, dir_slash
    '''use os.system and ffmpeg to copy sound from video'''
    if new_name == None:
        new_name = video_filename
    if mode == 'copy':
        os.system(f'ffmpeg -i "{video_filename}" -y -loglevel quiet -vn -acodec copy {frames_path+dir_slash}audio.aac')
    elif mode == 'paste':
        os.system(f'ffmpeg -i "{video_filename}"  -y -loglevel quiet -i {frames_path+dir_slash}audio.aac -map 0:v -map 1:a -c:v copy "{new_name}"\ny\n')

def print_image(image):
    '''includes convert to text'''
    image = image.resize((image.size[0]*3, image.size[1]))
    target_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
    if image.size[0] / target_size[0] > image.size[1] / target_size[1]:
        multi = image.size[0] / target_size[0]
        image = image.resize((target_size[0], int(image.size[1] // multi)))
    else:
        multi = image.size[1] / target_size[1]
        image = image.resize((int(image.size[0] // multi), target_size[1]))
    pixels = image.load()
    
    text = convert_pixels_to_text(image, image.size, only_text = True,color_mode_f = True).splitlines()[1:]
    output = '\033[38;2;0;0;255mimage resolution is relative to the console size, set the font size lower for better quality\033[0m\n\n'
    if color_mode:
        for row in tqdm(range(image.size[1]), leave=True, desc = f'size is {image.size}',colour = '#00FFFF'):
            black = False
            for pixel in range(image.size[0]):
                colors = pixels[pixel, row]
                text_var = text[row][pixel*2]
                output += f'\033[38;2;{colors[0]};{colors[1]};{colors[2]}m{text_var}'
                if text_var != ' ': black = False
            output += '\x1b[0m\n'
            if black == True:
                output = '\n'.join(output.splitlines()[:-1])
                print('rm line', len(output.splitlines()))
        print(output)
    else:
        for line in text:
            print(line[::2])

print('\033[32;5m\033[38;2;0;0;255mloading color values\033[0m', end = '\r')
colors, max_color = get_values()
#sort colors by value of the letter
if True: #process colors
    multi = max_color/255
    colors2 = {}
    for key in colors.keys():
        colors[key] = int(colors[key]/multi)
        colors2[int(int(colors[key]/multi)//5 * 5)] = key
    colors = {k: v for k, v in sorted(colors.items(), key=lambda item: item[1])}
    if 0 in colors.values():
        del colors[list(colors.keys())[list(colors.values()).index(0)]]
        colors[' ']=0
    val = {}
    for key, value in colors.items():
        val[key] = value
    keys_num = list(val.keys())
    values_num = [val[x] for x in keys_num]
    
    val_based = {}
    for num in range(0, 256):
        val_based[num] = list(colors.keys())[list(colors.values()).index(min(values_num, key=lambda l:abs(l-num)))]
    
new_frames = []
print('\033[32;5m\033[38;2;255;255;0mchoose file\033[0m' + ' ' * 15, end = '\r')
path = get_path(video=font_mode)
if path == '' or type(path) == tuple:
    print('\033[38;2;255;0;0mno file provided, exiting...\033[0m')
    quit()
c_imgs = []
if (path.endswith('.avi') or path.endswith('.mov') or path.endswith('.mp4')) and font_mode:
    frames_pil, fps, length = load_video(path, video_width)

    try:
        os.mkdir(frames_path)
    except FileExistsError:
        #delete all from the frames directory
        for image in os.listdir(frames_path):
            os.remove(frames_path+dir_slash + image)
    
    if ffmpeg: copy_sound_from_video(path)
    if not 'audio.aac' in os.listdir(frames_path):
        ffmpeg = False
        #idk y, but videos without sound, get flipped upside down
        for frame in range(len(frames_pil)):
            frames_pil[frame] = frames_pil[frame].transpose(Image.Transpose.ROTATE_180)
    next_img = ['placeholder', Image.new('RGB', (1, 1), 'black')]
    longest, end = convert_pixels_to_text(frames_pil[0], frames_pil[0].size, return_len_end=True)
    frame_size = frames_pil[0].size
    last_backup_name = None
    for selected_frame in tqdm(range(len(frames_pil)), f'\033[38;2;0;255;0mconverting \033[38;2;0;0;255m{"*".join([str(x) for x in frame_size])}\033[38;2;0;255;0m pixels per frame to text\033[0m', colour = '#00ff00'):
        img = convert_pixels_to_text(frames_pil[selected_frame], frame_size, longest=longest, end=end, color_mode_f=color_mode)
        next_img = [frames_pil[selected_frame], img]

        if len(str(selected_frame)) >7:
            img.save(frames_path+dir_slash+'frame' + str(selected_frame) + '.jpg')
        else:
            img.save(frames_path+dir_slash+f'frame{(7 - len(str(selected_frame))) * "0"}' + str(selected_frame) + '.jpg')
        
        if selected_frame % 1500 == 0 and selected_frame > 0:
            create_video(frames_path, fps, dir_path + dir_slash + f'ascii video backup{" - loading sound" if ffmpeg else f" {selected_frame} out of {len(frames_pil)}"}', 'creating backup video')
            if last_backup_name != None:
                try:
                    os.remove(last_backup_name)
                except Exception as e: print(e)

                if ffmpeg: copy_sound_from_video(dir_path + dir_slash + 'ascii video backup - loading sound.avi', 'paste', dir_path + dir_slash + f'ascii video backup {selected_frame} out of {len(frames_pil)}.avi')
                last_backup_name = dir_path + dir_slash + f'ascii video backup {selected_frame} out of {len(frames_pil)}.avi'
                try:
                    os.remove(dir_path + dir_slash + 'ascii video backup - loading sound.avi')
                except Exception as e: print(e)
        frames_pil[selected_frame] = None
    if last_backup_name != None:
        try:
            os.remove(last_backup_name)
        except Exception as e: print(e)

    if ffmpeg:
        create_video(frames_path, fps, dir_path + dir_slash + f'ascii video - loading sound', '\033[32;5m\033[38;2;255;255;0mexporting final video\033[0m', leave=True)
        print('\033[38;2;0;0;255madding sound to video...\033[0m', end = '\r')
        copy_sound_from_video(dir_path + dir_slash + 'ascii video - loading sound.avi', 'paste', dir_path + dir_slash + 'ascii video.avi')
        os.remove(dir_path + dir_slash + 'ascii video - loading sound.avi')
    else:
        create_video(frames_path, fps, dir_path + dir_slash + 'ascii video', 'creating final video', leave=True)
    print('\033[48;2;0;255;0m\033[32;5mdone\033[0m' + ' '*25)
    for frame in os.listdir(frames_path):
        os.remove(frames_path + dir_slash+frame)
    os.rmdir(frames_path)
    try:
        os.remove(dir_path + dir_slash + 'ascii video - loading sound.avi')
    except FileNotFoundError: pass #sometimes the file exists
    webbrowser.open(dir_path + dir_slash + 'ascii video.avi')


else:
    try:
        img = Image.open(path).convert('RGBA')
        rgb_frame = Image.new('RGBA', img.size, 'white')
        try:
            rgb_frame.paste(img, (0, 0), img)
        except ValueError as e:
            frame = img
            print(e)
        print_image(rgb_frame)

        frame = rgb_frame.convert('L')
        frame = fit_size(fit_size(frame).resize((int(frame.width * (video_width / frame.height)), video_width)))
        size = frame.size
        if font_mode:
    
            text, image = convert_pixels_to_text(frame, size, True, once=True)
            if color_mode:
                image = add_colors(rgb_frame, image)
            image.save(dir_path+dir_slash+'text-image.png')
            print(f"\n\033[38;2;0;255;0mimage of the text saved to \033[32;4m{dir_path+dir_slash+'text-image.png'}\033[0m")
        
        else:
            text = convert_pixels_to_text(rgb_frame.convert('L'), size, only_text=True)
        print(f"\n\033[38;2;0;255;0mtext saved to \033[32;4m{dir_path+dir_slash+'text-image.txt'}\033[0m")
        with open(dir_path+dir_slash+'text-image.txt', 'w') as f:
            f.write(text)
        
    except UnidentifiedImageError:
        print(path, f'\033[38;2;255;0;0mis not a {"video or " if font_mode else ""}image\033[0m')
