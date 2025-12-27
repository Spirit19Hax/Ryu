# ===== IMPORTS =====
from colorama import Fore, Back, Style, init
init()
from pytubefix import YouTube
import re 
import subprocess
import os

# ===== FUNCTION DEFINITIONS =====   
def on_progress(stream, chunk, bytes_remaining):
    try:
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        print(f"\r{Fore.CYAN}Downloading: {percentage:.1f}%", end='', flush=True)
    except:
        pass

def show_banner():
    ascii_art = """
 _______                   
(  ____ )|\\     /||\\     /|
| (    )|( \\   / )| )   ( |
| (____)| \\ (_) / | |   | |
|     __)  \\   /  | |   | |
| (\\ (      ) (   | |   | |
| ) \\ \\__   | |   | (___) |
|/   \\__/   \\_/   (_______)
    """
    print(Fore.CYAN + ascii_art)
    print(Fore.YELLOW + "    YouTube Video Downloader Tool")
    print(Fore.GREEN + "         Made with 🔥\n")

def get_youtube_url():
    while True:
        try:
            link = input("Paste the YouTube URL here: ").strip()
            yt = YouTube(link, on_progress_callback=on_progress)
            print(Fore.CYAN + "⏳ Hold up... Checking the video...")
            title = yt.title
            print(Fore.GREEN + f"✓ Nice! Found: {title}")
            return yt
        except Exception as e:
            print(Fore.RED + f"✗ Error: {e}")
            print(Fore.YELLOW + "Please try again with a valid YouTube URL")
            
def get_filtered_stream(yt):
    resolution_dic = {}
    audio = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    res = yt.streams.filter(only_video=True,).order_by("resolution").desc()
    for stream in res:
        current_res = stream.resolution
        if current_res not in resolution_dic:
            resolution_dic[current_res] = stream
        else:
            stored_stream = resolution_dic[current_res]
            stored_codecs = stored_stream.codecs[0]
    return resolution_dic, audio

def display_option(resolution):
    for i,(res, stream) in enumerate(resolution):
        size = stream.filesize / (1024*1024)
        size_str = f'{size: .2f} MB'
        print(f"{i+1}. {res} | {stream.codecs[0]} | {size_str}")

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True)
        return True
    except Exception as e:
        print(Fore.RED + f"✗ Error: {e}")
        return False

def get_user_choice(resolution):
    while True:
        try:
            choice = int(input("Select Stream: ")) - 1
            if 0 <= choice < len(resolution):
                selected_res = resolution[choice]
                selected_stream = selected_res[1]
                return selected_stream
            else:
                print(Fore.RED + "✗ Choice Don't Exist!")
        except ValueError:
            print("Use The Proper Index Number")
            
def download(selected_stream, audio, video_path, audio_path):
    try:
        selected_stream.download(output_path=video_path, filename = f"raw_video.mp4")
        audio.download(output_path=audio_path, filename = f"raw_audio.mp3")
        return True
    except Exception as e:
        print(Fore.RED + f"✗ Download failed: {e}")
        return False

def merge_video_audio(video_path, audio_path, output):
    try:
        merge = [
            "ffmpeg",
            "-i", video_path,      # input video
            "-i", audio_path,      # input audio
            "-c:v", "copy",        # copy video stream
            "-c:a", "aac",         # encode audio to aac
            "-strict", "experimental", 
            output
        ]

        subprocess.run(merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Video Saved In: {output}", True
    except subprocess.CalledProcessError:
      return "Merge failed! Check FFmpeg or file paths.", False

def cleanup_temp_files(video_path, audio_path):
    if os.path.exists(video_path):
        os.remove(video_path)
    else:
        print("No video found")
        
    if os.path.exists(audio_path):
        os.remove(audio_path)
    else:
        print("No audio found")
    return "Temp Sucessfully Deleted"

# ===== MAIN WINDOW =====

# ===== MAIN EXECUTION =====
show_banner()
if check_ffmpeg():
    yt = get_youtube_url()

    resolution_dic, audio = get_filtered_stream(yt)

    display_option(list(resolution_dic.items()))

    selected_stream = get_user_choice(list(resolution_dic.items()))

    clear_title = re.sub(r'[\//*?:"<>|]', "", yt.title)

    if download(selected_stream, audio, r"D:/Youtube Tool py/temp vid", r"D:/Youtube Tool py/temp aud"):
        merge_video_audio(r"D:/Youtube Tool py/temp vid/raw_video.mp4", r"D:/Youtube Tool py/temp aud/raw_audio.mp3", fr"D:/Youtube Tool py/Final/{clear_title}.mp4")
        cleanup_temp_files(r"D:/Youtube Tool py/temp vid/raw_video.mp4", r"D:/Youtube Tool py/temp aud/raw_audio.mp3")
    else:
        print(Fore.RED + "✗ Download Failed")
else:
    print(Fore.RED + "✗ FFmpeg not installed! Please install FFmpeg first.")

