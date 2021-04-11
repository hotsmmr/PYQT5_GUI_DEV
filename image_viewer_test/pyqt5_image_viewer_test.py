from PyQt5.QtWidgets import *
from main_tab import MainTab

class PyQt5ImageViewerTest(QMainWindow):
    def __init__(self, canvas_width, canvas_height):
        super().__init__()

        # define window parameters
        self.title = "PyQt5ImageViewerTest"
        self.left = 100
        self.top = 100
        self.width = canvas_width
        self.height = canvas_height * 2
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # define tabs widgets
        self.tabs = QTabWidget()
        self.main_tab = MainTab(canvas_width, canvas_height)

        # add tabs
        self.tabs.addTab(self.main_tab,"main")

        # define original signal to slot
        self.setCentralWidget(self.tabs)

        self.show()