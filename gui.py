from tkinter import *
from tkinter.ttk import *
from utils import *

class MainApplication(Tk):
    def __init__(self, app, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.app = app
        self.resizable(False, False)
        self.title("Simple Youtube Downloader")

        self.control_frame = ControlFrame(self)
        self.control_frame.pack(side=TOP, fill=X)

        self.url_label = Label(self, text="Paste URL:")
        self.url_label.pack()

        self.url_entry = Entry(self)

        #get clipboard content
        #if it is a youtube url, add it to the url_entry
        try:
            clip = self.clipboard_get()
            if youtube_url_validation(clip):
                self.url_entry.insert(0, clip)
                self.url_entry.selection_range(0, END)
        except:
            pass
        
        self.url_entry.bind("<Return>", self.handleURL)
        self.url_entry.pack(
            fill=X,
            expand=True,
            padx=5,
            pady=5,
            ipadx=100
        )

        self.tabs = []

        #focus
        self.url_entry.focus_set()

    def handleURL(self, event=None):
        url = self.url_entry.get()
        if not youtube_url_validation(url):
            return
        self.app.manager.addTab(url)
        self.url_entry.delete(0, END)

    def addTab(self, tab):
        uitab = TabFrame(self, tab)
        self.tabs.append(uitab)
        uitab.pack(side=TOP, fill=BOTH, expand=True)
        return uitab

class ControlFrame(Frame):
    def __init__(self, parent) -> None:
        Frame.__init__(self, parent)
        self.parent = parent

        self.stop_btn = Button(self, text="Stop all", command=self.stop)
        self.stop_btn.grid(row=0, column=0, padx=5, pady=5)

    def stop(self):
        self.parent.app.manager.stopAll()
        self.focus()

class TabFrame(LabelFrame):
    def __init__(self, parent, url) -> None:
        LabelFrame.__init__(self, parent, text="Loading...")
        self.parent = parent
        self.url = url

        self.title_label = Label(self, text="Loading...")
        self.percent_label = Label(self, text="0%")
        self.progress_bar = Progressbar(self, orient=HORIZONTAL, length=200)
        self.mp4_btn = Button(self, text="Loading...", command=self.mp4, state="disabled")
        self.close_btn = Button(self, text="Close", command=self.close)

        self.title_label.pack()
        self.percent_label.pack()
        self.progress_bar.pack()
        self.mp4_btn.pack()
        self.close_btn.pack()

    def mp4(self):
        self.parent.app.manager.mp4(self.url)
        self.focus()

    def stop(self):
        self.parent.app.manager.stopTab(self.url)
        self.focus()

    def close(self):
        self.parent.app.manager.closeTab(self.url)