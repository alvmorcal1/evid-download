import tkinter as tk
from tkinter import ttk
import sys
import os
from PIL import ImageTk, Image
import requests
import threading

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(src_path)
from py_easy_downloader import easydownloader

class App(tk.Tk):
    """
    Basic class of Tkinter that creates main window and displays it.

    Object-oriented approach.
    """
    def __init__(self):
        super().__init__()
        self.geometry("854x480")
        self.resizable(False,False)
        self.title("Easy VDownloader")

        #   Globals vars for 'OptionMenu()' must be declared here
        self.language_option_var = tk.StringVar(self)  
        self.selected_resolution_var = tk.StringVar(self)
        self.selected_format_var = tk.StringVar(self)

        #   Globals vars
        self.video_image = None #   Image must be declared here or don't work.
        self.video_info_labels = []
        self.file_name_entry = None
        self.resolution_id = None
        self.video_format = "Default format"
        self.downloading_information = None

        self.formats = ("Default format", "mp4", "mkv", "avi", "webm")

        self.languages = ("Español", "English")              
        self.language = "en"
        self.translations = {
            "es": {"title": "Easy VDownloader", "url_button": "Buscar", "file_name_entry": "Nombre de archivo"},
            "en": {"title": "Easy VDownloader", "url_button": "Search", "file_name_entry": "File name"}
        }
        self.url_entry_placeholders = {
            "en": "Video URL",
            "es": "URL del video a descargar"
        }   
        self.file_name_entry_placeholders = {
            "en": "File name",
            "es": "Nombre del archivo"
        }

        #   Calling base widget creator.
        self.create_widgets()
        self.translate()

    def translate(self):
        """
        Change the 'text' property of every widget to fit the selected language.
        """
        self.url_button.config(text=self.translations[self.language]["url_button"])
        self.url_entry.change_language(self.language)
        self.file_name_entry.change_language(self.language)

    def create_widgets(self):
        """
        Creates widgets for the application interface.
        """
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column= 0,sticky="news")        

        #   Creating custom object using 'EntryWithPlaceholder' class.
        self.url_entry = EntryWithPlaceholder(frm, placeholders=self.url_entry_placeholders, width=85)
        self.url_entry.grid(column=0,row=0, padx=10)
        
        self.file_name_entry = EntryWithPlaceholder(frm, placeholders=self.file_name_entry_placeholders, width=85)

        #   Calling search_url with the value entered by the user in the entry when the button is clicked.
        self.url_button = ttk.Button(frm, text="Search", command=lambda: search_url(self, self.video_info_labels, frm, self.url_entry))
        self.url_button.grid(column=1,row=0)

        #   Language menu to change application appearance depending on language.
        language_menu = ttk.OptionMenu(
            self,
            self.language_option_var,
            self.languages[1],
            *self.languages,
            command=self.language_changed
        )
        language_menu.place(relx=1, rely=1, anchor='se', x=-10, y=-10)
    
    def language_changed(self, *args):
        """
        When the language is changed, 'self.translate()', which changes application texts, is called.
        """
        if self.language_option_var.get() == "English":
            self.language = "en"
        elif self.language_option_var.get() == "Español":
            self.language= "es"
        
        self.translate()    

    def refresh_information(self):
        """
        Refreshes video information label to avoid conflict.
        """
        for label in self.video_info_labels:
            label.destroy()
        self.video_info_labels.clear()    

    def format_changed(self, *args):
        self.video_format = args[0]
        print(self.video_format)

    def confirm_resolution(self, option, video_info, *args):
        video_info = video_info.replace('p','')
        self.resolution_id= args[0][int(video_info)][1]
        print(self.resolution_id)


class EntryWithPlaceholder(ttk.Entry):
    """
    Custom Entry class that allows the use placeholders.
    """
    def __init__(self, master=None, placeholders={}, default_language="en", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholders = placeholders
        self.default_language = default_language
        self.current_language = default_language
        self.placeholder_color = "grey"
        self.normal_color = self["foreground"]
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.put_placeholder()

    def _on_focus_in(self, event):
        if self.get() == self.placeholders[self.current_language]:
            self.delete(0, tk.END)
            self["foreground"] = self.normal_color

    def _on_focus_out(self, event):
        if not self.get():
            self.put_placeholder()

    def put_placeholder(self):
        placeholder_text = self.placeholders.get(self.current_language, "")
        self.insert(0, placeholder_text)
        self["foreground"] = self.placeholder_color

    def change_language(self, language):
        self.current_language = language
        self.delete(0, tk.END)
        
        #   self.master.focus_force() force focus on the root window, removing focus from other widgets.
        self.master.focus_force()
        self.put_placeholder()

def download_audio(self, file_name, resolution_id, video_format, url, download_button, frm, video_info_labels, download_audio_button, title):
    if self.downloading_information != None:
        self.downloading_information.config(text="")
        
    if not file_name or any(file_name in values for values in self.file_name_entry_placeholders.values()):
        file_name = title
    
    download_button.config(state="disable")
    download_audio_button.config(state="disable")
    
    print(file_name, resolution_id, video_format)
    print(url)

    self.downloading_information = ttk.Label(frm, text="Only Audio Download Started")
    self.downloading_information.grid(row=8)

    video_info_labels.append(download_audio_button)
    video_info_labels.append(self.downloading_information)
    video_info_labels.append(download_button)

    thread = threading.Thread(target=easydownloader.audio_downloader, args=(url,resolution_id, self.downloading_information, download_button, video_format,file_name,download_audio_button))
    thread.start()

    return None

def handle_download(self,frm, video_info_labels, url,title):
    if self.downloading_information != None:
        self.downloading_information.config(text="")

    self.file_name_entry.grid(row=5, pady=10)

    format_menu = ttk.OptionMenu(
        frm,
        self.selected_format_var,
        self.formats[0],
        *self.formats,
        command=self.format_changed
    )    

    download_button = ttk.Button(frm, text="Download", command=lambda: download_video(self, self.file_name_entry.get(), self.resolution_id, self.video_format, url, download_button, frm, video_info_labels,title, download_audio_only))
    download_button.grid(row=5, column=1)

    download_audio_only = ttk.Button(frm, text="Audio Only", command=lambda: download_audio(self, self.file_name_entry.get(), self.resolution_id, self.video_format, url, download_button, frm, video_info_labels, download_audio_only, title))
    download_audio_only.grid(row=6, column=1)
    format_menu.grid(row=4,column=1, padx=0,sticky="w")

    video_info_labels.append(format_menu)
    video_info_labels.append(download_button)
    video_info_labels.append(download_audio_only)
    video_info_labels.append(self.downloading_information)

def download_video(self, file_name, resolution_id, video_format, url, download_button, frm, video_info_labels, title, download_audio_button):
    
    if self.downloading_information != None:
        self.downloading_information.config(text="")

    if not file_name or any(file_name in values for values in self.file_name_entry_placeholders.values()):
        file_name = title
    
    if not resolution_id:
        return None
    
    download_button.config(state="disable")
    download_audio_button.config(state="disable")
    print(file_name, resolution_id, video_format)
    print(url)

    self.downloading_information = ttk.Label(frm, text="Download Started")
    self.downloading_information.grid(row=8)
    thread = threading.Thread(target=easydownloader.video_downloader, args=(url,resolution_id, self.downloading_information, download_button, video_format,file_name, download_audio_button))
    thread.start()

    video_info_labels.append(download_button)
    video_info_labels.append(self.downloading_information)

def search_url(self, video_info_labels, frm, entry):
    """
    Calls the 'easydownloader.video_info()' function, which obtains video info from URL.
    
    Parameters:
    - entry (tk.Entry): The Tkinter Entry widget containing the URL entered by the user.
    """

    if not entry.get() or any(entry.get() in values for values in self.url_entry_placeholders.values()):
        return None
    
    self.refresh_information()

    url = entry.get()
    video_info = easydownloader.video_info(url)

    title = video_info[1]['title']
    uploader = video_info[1]['uploader']
    duration = video_info[1]['duration']
    thumbnail = video_info[1]['thumbnail']

    title_label = ttk.Label(frm,text=title, width=85)
    title_label.grid(row=1,column=0, padx=10, sticky="w")

    uploader_label = ttk.Label(frm, text=uploader)
    uploader_label.grid(row=2,column=0, padx=10, sticky="w")

    duration_label = ttk.Label(frm, text=duration)
    duration_label.grid(row=4,column=0, padx=10, sticky="w")

    video_resolutions = [str(x) + "p" for x in video_info[0].keys()]
    video_resolutions_label = ttk.OptionMenu(frm, self.selected_resolution_var, "Select resolution", *video_resolutions, command=lambda option: self.confirm_resolution(self, option, video_info[0]))
    video_resolutions_label.grid(row=4,column=0, padx=17,sticky="e")

    try:            
        video_thumbnail = Image.open(requests.get(thumbnail, stream=True).raw)
        video_thumbnail = video_thumbnail.resize((256,144))
        self.video_image = ImageTk.PhotoImage(video_thumbnail)
        label_image = ttk.Label(frm,image=self.video_image)
        label_image.grid(row=3,column=0, padx=10, sticky="w")
    except:
        label_image = ttk.Label(frm,image=None)
        label_image.grid(row=3,column=0, padx=10, sticky="w")

    video_info_labels.append(title_label)
    video_info_labels.append(uploader_label)
    video_info_labels.append(duration_label)
    video_info_labels.append(video_resolutions_label)
    video_info_labels.append(label_image)

    handle_download(self,frm,video_info_labels,url,title)

if __name__ == "__main__":
    """
    By default, this archive creates an object of type 'App()', and calls the 'mainloop()' method, which displays the window.
    """
    app = App()
    app.mainloop()