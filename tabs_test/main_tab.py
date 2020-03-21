import pandas as pd
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MainTab(QWidget):

    procStart = QtCore.pyqtSignal(str, object)

    def __init__(self, func_info_csv):
        super().__init__()

        # setting ui parameters
        self.layout = QVBoxLayout()

        # create dataframe from input csv
        self.input_df = pd.read_csv(func_info_csv).sort_values("function", ascending=True)
        
        # define widgets
        self.wdgts_list = []
        self.wdgt_quit_button = None
        
        # to output code
        self.function = ""
        self.output_df = None
        
        # create list
        self.createList(self.input_df, "function")
        self.createQuitButton()

        # create layout
        self.updateLayout()

    def updateLayout(self):
        # add list to layout
        for wdgt_list in self.wdgts_list:
            self.layout.addWidget(wdgt_list) 
        self.layout.addWidget(self.wdgt_quit_button) 
        self.setLayout(self.layout)

    def createList(self, df, column):
        self.wdgts_list.append(QListWidget(self))
        for value in df[column].values:
            # set item to list
            self.wdgts_list[-1].addItem(str(value))
            # set connect method
        self.wdgts_list[-1].itemDoubleClicked.connect(self.list_click)

    def createQuitButton(self, text="Quit"):
        # Create botton
        self.wdgt_quit_button = QPushButton(text, self)
        self.wdgt_quit_button.clicked.connect(QCoreApplication.instance().quit)

    @pyqtSlot()
    def list_click(self):
        # get signal
        sender = self.sender()

        # slice dataframe by clicked function name
        self.function = sender.currentItem().text()
        self.output_df = self.input_df[self.input_df["function"] == self.function].copy()

        self.procStart.emit(self.function, self.output_df)
