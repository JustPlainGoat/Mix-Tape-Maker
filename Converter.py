from __future__ import unicode_literals
from tkinter import *
import youtube_dl
import urllib
import re
import os
import shutil
import threading
import getpass
import subprocess

youtube_dl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

song_list = []
# desktop_path = "C:\\Users\\Luke\\Desktop\\"
desktop_path = "/Users/" + getpass.getuser() + "/Desktop/"


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Mix-tape Maker")
        master.geometry("750x500")

        self.label = Label(master, text="Enter file name for the song list: ")
        self.label.pack()

        self.entry = Entry(master, width=45)
        self.entry.pack()

        self.label_title = Label(master, text="Title of Mixtape: ")
        self.label_title.pack()

        self.entry_title = Entry(master, width=45)
        self.entry_title.pack()

        self.button = Button(master, text="Download", command=self.download_button_click)
        self.button.pack()

        self.label_help = Label(master, text="\nHOW TO USE:\n1. Create a text file on your desktop listing each song you want line by line."
                                             "\n2. Enter the text file name inside the top most box.\n3. Give a title to your mixtape.\n"
                                             "4. Click download and the mixtape will be created on your desktop."
                                             "\n-----------------------------------------------------------------------------------\n")
        self.label_help.pack()

        self.text = Text(master)
        self.text.pack()

    def download_button_click(self):
        global song_list
        song_list = self.read_file(self.entry.get())

        thread = DownloadVideosThread(self.text)
        thread.start()

    def read_file(self, file_name):
        global desktop_path
        file = desktop_path + file_name

        self.update_text_widget("Reading file " + self.entry.get())

        with open(file, "r") as f:
            songs = f.read().splitlines()
        # change to "\\" for windows
        desktop_path += self.entry_title.get() + "/"

        self.update_text_widget("\nFound " + str(len(songs)) + " songs!")

        return songs

    def update_text_widget(self, message):
        self.text.insert(END, message)
        self.text.see(END)


class DownloadVideosThread(threading.Thread):
    def __init__(self, text):
        threading.Thread.__init__(self)
        self.text = text

    def run(self):
        video_urls = self.find_video_urls(song_list)
        self.download_videos(video_urls, song_list)
        # self.create_desktop_directory(song_list)

    def update_text_widget(self, message):
        self.text.insert(END, message)
        self.text.see(END)

    def find_video_urls(self, songs):
        videos = list()
        for song in songs:
            self.update_text_widget("\nSong - " + song + " - Querying youtube results ...")

            query_string = urllib.parse.urlencode({"search_query": song})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

            if len(search_results) is not 0:
                videos.append("https://www.youtube.com/watch?v=" + search_results[0])
                self.update_text_widget("\nSong - " + song + " - Found top result!")

        return videos

    def download_videos(self, urls, songs):
        self.update_text_widget("\n\nStarting downloads ...")
        index = 0
        for url in urls:
            self.update_text_widget("\nSong - " + songs[index]
                                    + " - Extracting audio from video at " + url + " ...")
            '''with youtube_dl.YoutubeDL(youtube_dl_options) as ydl:
                ydl.download([url])'''
            subprocess.call(
                ['youtube-dl', '-o', desktop_path + songs[index] + '.mp3',
                 "--extract-audio", "--audio-format", "mp3", url])

            self.update_text_widget("\nSong - " + songs[index] + " - Download complete!")
            index += 1

        self.update_text_widget("\n\nAll downloads complete! Check your desktop for your mixtape!")

    '''def create_desktop_directory(self, songs):
        self.update_text_widget("\n\nPushing mixtape to desktop ...")

        if not os.path.exists(desktop_path):
            os.makedirs(desktop_path)

        # program_path = "C:\\Users\\Luke\\PycharmProjects\\MixtapeMaker\\"
        program_path = "/Users/michael/PycharmProjects/MixtapeMaker/"
        contents = os.listdir(program_path)

        song_number = 0
        for content_part in contents:
            filename, file_extension = os.path.splitext(program_path + content_part)
            if file_extension == ".mp3":
                shutil.move(program_path + content_part, desktop_path + songs[song_number] + ".mp3")
                song_number += 1
        self.update_text_widget("\nMixtape is complete, enjoy!")'''

root = Tk()
root.resizable(width=False, height=False)
gui = GUI(root)
root.mainloop()



