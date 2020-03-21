from PyQt5.QtWidgets import *
from main_tab import MainTab
from sub1_tab import Sub1Tab
from sub2_tab import Sub2Tab

class PyQt5TabsTest(QMainWindow):
    def __init__(self, func_info_csv, args_info_csv, gl_vars_info_csv):
        super().__init__()

        # define window parameters
        self.title = "PyQt5TabsTest"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 480
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # define tabs widgets
        self.tabs = QTabWidget()
        self.main_tab = MainTab(func_info_csv)
        self.sub1_tab = Sub1Tab(args_info_csv)
        self.sub2_tab = Sub2Tab(gl_vars_info_csv)

        # add tabs
        self.tabs.addTab(self.main_tab,"main")
        self.tabs.addTab(self.sub1_tab,"sub1")
        self.tabs.addTab(self.sub2_tab,"sub2")

        # define original signal to slot
        self.main_tab.procStart.connect(self.sub1_tab.update_table)
        self.main_tab.procStart.connect(self.sub2_tab.update_table)
        self.setCentralWidget(self.tabs)

        self.show()
