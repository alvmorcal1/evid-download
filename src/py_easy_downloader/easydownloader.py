## Core of the python app that makes the basic logic (using yt_dlp python library)
import sys
import yt_dlp
import os
from urllib.request import urlretrieve
import zipfile
import shutil
import re
import subprocess

def info_from_url(url, opts={}):
    """
    Obtain info from url using yt_dlp.

    Parameters:
    - url (str): Video URL.
    - opts (dict): Yt_dlp options if needed.

    Returns:
    - dict: Containing direct info of url from yt_dlp.
    """
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def video_info_parser(info):
    """
    Since yt_dlp info is big and parsed in a specific way, this function parses only needed info

    Parameters:
    - info (dict): Direct obtained from yt_dlp.extract_info().

    Returns: 
    - parsed_info: Custom dict with 'title', 'webpage', 'uploader', 'duration', 'american_upload_date' and 'international_upload_date' params.
    """
    date = info.get('upload_date',0)
    if date != 0:    
        upload_date = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
        international_upload_date = date[6:8] + '-' + date[4:6] + '-' + date[0:4]

    duration = info.get('duration', 0)
    duration_formated = str(duration // 3600) + "h, " + str((duration % 3600) // 60) + "min, " + str(duration % 60) + "s."

    list_formats = []
    for format in info.get('formats'):
        list_formats.append(format['format'])

    parsed_info = {
        'title': info.get('title', ''),
        'webpage_url': info.get('webpage_url', ''),
        'uploader': info.get('uploader', ''),
        'duration': duration_formated,
        'american_upload_date': upload_date,
        'international_upload_date': international_upload_date,
        'thumbnail': info.get('thumbnail')
    }
    return parsed_info

def video_info(url):
    """
    Receives a URL and returns a dictionary with resolutions
    as keys and values as a list [bitrate, format id].

    This function aims to obtain best bitrate video of every resolution available (In the case that there are some formats for the same resolution).

    Parameters:
    - url (str): The URL of the video.

    Returns:
    - dict: A dictionary containing resolutions as keys and a list [bitrate, format-id] as values.
    """
    opts = {
    }

    video_information = info_from_url(url,opts)
    video_information_parsed = video_info_parser(video_information)
    best_quality_format = {}
    for format in video_information.get('formats'):

        quality = format.get('height', 0)
        tbr = format.get('tbr', 0)
        format_id = format.get('format_id', 0)

        if quality == None or quality == 0 or tbr == None or tbr == 0:
            pass        
        elif quality not in best_quality_format:
            best_quality_format[quality] = [tbr,format_id]
        elif best_quality_format[quality][0] < tbr:
            best_quality_format[quality] = [tbr,format_id]

    return (best_quality_format,video_information_parsed)

def ffmpeg_check():
    ffmpeg_folder = './src/py_easy_downloader/ffmpeg'
    temp_ffmpeg = '.temp/ffmpeg-master-latest-win64-gpl/bin/'
    zip_ffmpeg = '.temp/ffmpeg.zip'
    if os.path.isfile(ffmpeg_folder + "/ffmpeg.exe"): pass
    else:
        if not os.path.exists('.temp'): os.makedirs('.temp')
        print("Not Found ffmpeg.exe\n")

        print("Downloading lastest version from github . . .")

        urlretrieve('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
                    zip_ffmpeg)

        print("\nExtracting into temporal folder")
        
        with zipfile.ZipFile(zip_ffmpeg, 'r') as zip_temp:
            zip_temp.extractall('.temp')
        os.makedirs(ffmpeg_folder)
        if os.path.exists(temp_ffmpeg + 'ffmpeg.exe') and os.path.exists(temp_ffmpeg + 'ffplay.exe') and os.path.exists(temp_ffmpeg + 'ffprobe.exe'):
            shutil.copy(temp_ffmpeg + 'ffmpeg.exe', ffmpeg_folder)
            shutil.copy(temp_ffmpeg + 'ffplay.exe', ffmpeg_folder)
            shutil.copy(temp_ffmpeg + 'ffprobe.exe', ffmpeg_folder)
        
        os.remove(zip_ffmpeg)
        shutil.rmtree('.temp/ffmpeg-master-latest-win64-gpl')
        os.rmdir('.temp')

        print('Temporal folder has been removed')

        print('\nFFmpeg succesfully installed')

def video_downloader(url, format, label_info, button, extension_format, file_name, audio_button):
    ydl_opts = {
        'format': str(format)+'+bestaudio',
        'ffmpeg_location': "./src/py_easy_downloader/ffmpeg",
        'progress_hooks': [lambda d: download_progress(d, label_info, button)],
        'merge_output_format': 'mp4',
        'outtmpl': 'evid_downloads/'+file_name + '.%(ext)s'
    }

    print(extension_format)
    ffmpeg_check()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
    except:
        ydl_opts = {
            'format': str(format),
            'ffmpeg_location': "./src/py_easy_downloader/ffmpeg",
            'progress_hooks': [lambda d: download_progress(d, label_info, button)],
            'merge_output_format': 'mp4',
            'outtmpl': 'evid_downloads/'+file_name + '.%(ext)s'
    }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
    
    print(file_name)
    if extension_format != "Default format":
        subprocess.run(['ffmpeg', '-i', "evid_downloads/"+file_name+'.mp4', "evid_downloads/"+file_name+"."+extension_format])

    label_info.config(text="Video downloaded and converted")
    button.config(state="enabled")
    audio_button.config(state="enabled")

def download_progress(d, label, button):
    if d['status'] == 'downloading':
        percentaje = re.sub(r'\x1b\[[0-9;]*[mK]', '', d['_percent_str'])
        speed = re.sub(r'\x1b\[[0-9;]*[mK]', '', d['_speed_str'])
        print("Downloading", percentaje, speed)
        label.config(text="Downloading " + percentaje + " " + speed)
    elif d['status'] == 'finished':
        print("Download finished")
        label.config(text="Download Finished. Wait video conversion. If conversion takes so long, remember that depends on output format")
    return None

def audio_progress(d, label, button):
    if d['status'] == 'downloading':
        percentaje = re.sub(r'\x1b\[[0-9;]*[mK]', '', d['_percent_str'])
        speed = re.sub(r'\x1b\[[0-9;]*[mK]', '', d['_speed_str'])
        print("Downloading", percentaje, speed)
        label.config(text="Downloading " + percentaje + " " + speed)
    elif d['status'] == 'finished':
        print("Download finished")
        label.config(text="Converting Audio")
    return None

def audio_downloader(url, format, label_info, button, extension_format, file_name, audio_button):
    
    ydl_opts = {
        'format': 'bestaudio',
        'ffmpeg_location': "./src/py_easy_downloader/ffmpeg",
        'progress_hooks': [lambda d: audio_progress(d, label_info, button)],
        'outtmpl': 'evid_downloads/'+file_name + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }

    try:
        ffmpeg_check()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
    except:
        ydl_opts = {
            'ffmpeg_location': "./src/py_easy_downloader/ffmpeg",
            'progress_hooks': [lambda d: audio_progress(d, label_info, button)],
            'outtmpl': 'evid_downloads/'+file_name + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }]
        }

        ffmpeg_check()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    label_info.config(text="Audio Downloaded")
    button.config(state="enabled")
    audio_button.config(state="enabled")