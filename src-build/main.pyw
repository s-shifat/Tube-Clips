from pytube import YouTube, Playlist
import tkinter as tk
from tkinter.ttk import Progressbar
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from datetime import timedelta
import os
import time

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.yt = None
        self.playlist = None
        self.videos = []
        self.label = tk.Label(text='Enter the videos url: ', bg='#53717F', fg='#FFF2E3')
        self.label.grid(row=0, column=0, sticky='nsew', padx=10, pady=15)
        self.url = tk.StringVar()

        self.progressBar = Progressbar(orient= tk.HORIZONTAL, length=200, mode='indeterminate')
        self.progressBar.grid(row=1, column=1, columnspan=3 ,sticky='nsew')

        self.entry = tk.Entry(textvariable=self.url, width=50, fg='#53717F')
        self.entry.grid(row=0, column=1, sticky='nsew', pady=15)

        self.btn = tk.Button(text='Check', command=self.btnPressed, bg='#47A2FF', fg='#FFF2E3')
        self.btn.grid(row=0, column=2, sticky='nsew', padx=10, pady=15)

        self.download_button = tk.Button(text='Download', command=self.downloader, state=tk.DISABLED, bg='#91AAB7', fg='#FFF2E3')
        self.download_button.grid(row=6, column=0, columnspan=4, sticky='nsew', pady=15)
        
        self.vidInfo = tk.StringVar()
        self.display_header = tk.Label(textvariable=self.vidInfo, anchor='e', bg='#53717F', fg='#FBF2DB')
        self.vidInfo.set('Video information:')
        self.display_header.grid(row=2, column=0, columnspan=4, sticky='w', pady=5, padx=10)
    
        self.display = tk.Listbox(height=20, width=30, bg='#EDE4CE')
        self.display.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=10)
        self.hScroll = tk.Scrollbar(orient=tk.HORIZONTAL)
        self.vScroll = tk.Scrollbar()
        self.hScroll.grid(row=4, column=0, columnspan=4, sticky='ew', padx=10)
        self.vScroll.grid(row=3, column=4, sticky='ns')
        
        self.mp3 = tk.BooleanVar()
        self.mp4 = tk.BooleanVar()
        self.mp3.set(False)
        self.mp4.set(True)
        self.mp3OptionHolder = ttk.Checkbutton(text='Download Audio', state=tk.DISABLED, variable=self.mp3)
        self.mp4OptionHolder = ttk.Checkbutton(text='Download Video', state=tk.DISABLED, variable=self.mp4)
       
        self.mp3OptionHolder.grid(row=5, column=0, columnspan=1, sticky='ew', padx=10)
        self.mp4OptionHolder.grid(row=5, column=2, columnspan=1, sticky='ew')

        self.status = tk.Label(text='Status....')
        self.status.grid(row=7, column=0, columnspan=4 ,sticky='ew', padx=10, pady=15)  

        self.statusVar = tk.StringVar()
        self.statusDisplay = tk.Label(textvariable=self.statusVar)
        self.statusDisplay.grid(row=8, column=0, columnspan=4 ,sticky='ew', padx=10, pady=15)  

    def btnPressed(self):
        to_display = "Sorry! Video is not downloadable"
        try:
            to_display = ''
            self.progressBar.start(100)
            # self.yt = YouTube(self.url.get())
            try:
                self.videos = []
                self.yt = YouTube(self.url.get())
                self.playlist = False
                to_display += f" >> {self.yt.title} ||| DURATION: {timedelta(seconds=self.yt.length)}"
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, to_display)
                self.master.update()
                self.videos.append(self.yt)
            except:
                self.videos = []
                self.playlist = Playlist(self.url.get())
                self.yt = False
                self.display.delete(0, tk.END)
                to_display = self.vidInfo.get()
                to_display += f"\nPLAYLIST TITLE: {self.playlist.title}"
                self.vidInfo.set(to_display)
                for i, video in enumerate(self.playlist.videos):
                    to_display = f" {i+1}>> {video.title} ||| DURATION: {timedelta(seconds=video.length)}"
                    self.display.insert(tk.END, to_display)
                    self.videos.append(video)
                    self.master.update()
                    self.progressBar.step(30)

            self.display.config(yscrollcommand=self.vScroll.set)
            self.display.config(xscrollcommand=self.hScroll.set)
            self.vScroll.config(command=self.display.yview)
            self.hScroll.config(command=self.display.xview)
            self.download_button.config(state=tk.NORMAL, bg='#0077CC', fg='white')
            self.mp3OptionHolder.config(state=tk.NORMAL)
            self.mp4OptionHolder.config(state=tk.NORMAL)
            self.progressBar.stop()

        except:
            self.download_button.config(state=tk.DISABLED)

    def downloader(self):
        folderpath = askdirectory()
        self.progressBar.start()
        self.statusVar.set('Starting Download...')
        if len(self.videos) == 1:
            vidName = self.videos[0].title
            file=''
            if self.mp4.get():
                self.progressBar.step(30)
                self.statusVar.set(f'Downloading Video: {vidName}')
                self.master.update()
                self.videos[0].streams.get_highest_resolution().download(output_path=folderpath)
                self.statusVar.set('Downloading Video: complete!')
                self.master.update()
            if self.mp3.get():
                self.statusVar.set(f'Downloading Audio: {vidName}')
                self.progressBar.step(30)
                self.update()
                file = self.videos[0].streams.filter(only_audio=True).first().download(folderpath, vidName+' audio')
                self.statusVar.set('Downloading Audio: complete!')
                self.master.update()
            self.statusVar.set('File Downloaded Successfully!')
            self.changeExtension(file)
            time.sleep(3)
            os.startfile(folderpath)
        else:
            if self.mp3.get():
                audio_path = os.path.join(folderpath,f"{self.playlist.title}-AUDIO")
                try:
                    os.mkdir(audio_path)
                except FileExistsError:
                    pass
                for video in self.videos:
                    self.progressBar.step(30)
                    self.statusVar.set(f"Downloading Audio: {video.title}")
                    self.master.update()

                    file = video.streams.filter(only_audio=True).first().download(audio_path)

                    self.changeExtension(file)
                    self.statusVar.set(f"Downloading Audio: completed!")
                    self.master.update()
            if self.mp4.get():
                video_path = os.path.join(folderpath,f"{self.playlist.title}-VIDEO")
                try:
                    os.mkdir(video_path)
                except FileExistsError:
                    pass
                for video in self.videos:
                    self.progressBar.step(30)
                    self.statusVar.set(f"Downloading Video: {video.title}")
                    self.master.update()
                    
                    video.streams.get_highest_resolution().download(output_path=video_path)

                    self.statusVar.set(f"Downloading Video: completed!")
                    self.master.update()
            self.statusVar.set('All Files Downloaded!')
            time.sleep(3)
            os.startfile(folderpath)
        self.progressBar.stop()



    def changeExtension(self, filePath, extension='.mp3'):
        name, ext = os.path.splitext(filePath)
        try:
            os.rename(filePath, name + extension)
        except:
            pass


def main():
    root = tk.Tk()
    root.geometry('580x700')
    root.title('Tube Clips')
    root.iconbitmap('yt.ico')
    root.config(bg='#53717F')
    Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()
