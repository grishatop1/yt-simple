import os
import threading
import multiprocessing

import pytube
from pytube import request

class Tab:
    def __init__(self, manager, url):
        self.manager = manager
        self.url = url

        self.ready = False
        self.title = None
        self.author = None
        self.desc = None
        self.path = None
        self.yt = None
        
        self.f = None
        self.downloading = False
        self.size = None
        self.downloaded = 0
        self.stream = None
        self.stoppedIterator = True
        self.done = False

    def load(self):
        self.uitab = self.manager.app.gui.addTab(self.url)
        def loadThread():
            try:
                self.yt = pytube.YouTube(self.url)
                self.title = self.yt.title
                self.author = self.yt.author
                self.path = "videos/" + self.url[-11:] + ".mp4"
            except:
                self.uitab.config(text="Video is unavailable")
                self.uitab.title_label.config(text=f"{self.url}")
                self.uitab.mp4_btn.config(state="disabled", text="You can close the tab")
                return

            self.uitab.config(text=self.author)
            self.uitab.title_label.config(text=self.title)
            self.uitab.mp4_btn.config(state="normal", text="Download")
            self.ready = True

        thread = threading.Thread(target=loadThread)
        thread.daemon = True
        thread.start()

    def mp4(self):
        if self.downloading and self.done:
            return
        self.downloading = True
        self.uitab.mp4_btn.config(text="Stop", command=self.stop)
        if self.downloaded > 0:
            percent = self.downloaded / self.size * 100
            self.uitab.percent_label.config(text=str(round(percent, 2)) + "%")
            self.uitab.progress_bar.config(value=percent)
        def downloadThread():
            if not self.stream and not self.f:
                if os.path.exists(self.path):
                    os.remove(self.path)
                self.f = open(self.path, "ab")
                stream = self.yt.streams.get_highest_resolution()
                self.size = stream.filesize
                self.stream = request.stream(stream.url)
            
            if not self.stream: return
            if not self.stoppedIterator: return
            while self.downloading:
                self.stoppedIterator = False
                chunk = next(self.stream, None)
                self.stoppedIterator = True
                if chunk:
                    try:
                        self.f.write(chunk)
                    except:
                        self.stop()
                        try:
                            os.remove(self.path)
                        except:pass
                        try:
                            self.uitab.config(text="Error")
                            self.uitab.author_label.config(text="You can close the tab.")
                        except:pass
                        return
                    self.downloaded += len(chunk)
                else:
                    self.downloading = False
                    self.f.close()
                    self.f = None
                    self.done = True
                    self.uitab.percent_label.config(text="DONE :)")
                    self.uitab.mp4_btn.destroy()
                    break
                
                if self.downloading:
                    percent = self.downloaded / self.size * 100
                    display_percent = str(round(percent, 2)) + "%"
                    self.uitab.percent_label.config(
                        text=f"{display_percent} - {round(self.downloaded/1024/1024, 1)}MB/{round(self.size/1024/1024, 2)}MB"
                    )
                    self.uitab.progress_bar.config(value=percent)

        thread = threading.Thread(target=downloadThread)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.downloading = False
        try:
            self.uitab.mp4_btn.config(text="Continue", command=self.mp4)
            self.uitab.percent_label.config(text="PAUSED")
        except:pass


    def close(self):
        self.stop()
        if self.f:
            self.f.close()
        self.f = None
        self.uitab.destroy()

class Manager:
    def __init__(self, app) -> None:
        self.app = app
        self.tabs = {}
        self.downloading = False
        self.priority_tab = None

    def addTab(self, url):
        tab = Tab(self, url)
        if not url in self.tabs:
            self.tabs[url] = tab
            tab.load()

    def closeTab(self, url):
        self.tabs[url].close()
        del self.tabs[url]

    def stopTab(self, url):
        self.tabs[url].stop()

    def mp4(self, url):
        tab = self.tabs[url]
        #check if tab is ready
        if not tab.ready:
            return
        if self.priority_tab:
            self.priority_tab.stop()
        self.priority_tab = tab
        tab.mp4()
        self.downloading = True

    def stopAll(self):
        for tab in self.tabs.values():
            tab.stop()