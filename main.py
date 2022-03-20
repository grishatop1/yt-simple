import os
from manager import Manager
from gui import MainApplication

class App:
    def __init__(self):
        self.manager = Manager(self)
        self.gui = MainApplication(self)

    def run(self):
        os.makedirs("videos", exist_ok=True)
        self.gui.mainloop()
        
if __name__ == "__main__":
    app = App()
    app.run()