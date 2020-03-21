import os
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class TableTab(QWidget):
    def __init__(self, input_csv):
        super().__init__()

        # field
        self.target_column = "" # args or gl_vars
        self.target_columns = ["type", self.target_column, "value"]
        self.input_df = pd.read_csv(input_csv)
        if not "value" in self.input_df:
            self.input_df["value"] = str(0)
        self.function = "all"
        self.output_csv_file_name = ""
        self.output_df = self.input_df.copy()
        self.wdgt_file_name_label = None
        self.wdgt_file_name_edit = None
        self.wdgts_table = []
        self.wdgt_output_csv_button = None
        self.layout = QVBoxLayout()
        self.output_root = "tool_output"
        os.makedirs(self.output_root, exist_ok=True)

        self.createLineEdit()
        self.createOutputCsvButton()

    def updateLayout(self):
        # remove all widgets
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)
        # add label to layout
        self.layout.addWidget(self.wdgt_file_name_label) 
        # add line_edit to layout
        self.layout.addWidget(self.wdgt_file_name_edit)
        # add table to layout
        for wdgt_table in self.wdgts_table:
            self.layout.addWidget(wdgt_table)
        # add button to layout
        self.layout.addWidget(self.wdgt_output_csv_button) 
        self.setLayout(self.layout)

    def createLabel(self, text):
        self.wdgt_file_name_label = QLabel(text)

    def createLineEdit(self):
        self.wdgt_file_name_edit = QLineEdit()
        self.wdgt_file_name_edit.textChanged.connect(self.set_csv_file_name)

    def createTable(self, df, columns):
        # Create table
        self.wdgts_table.append(QTableWidget(self))
        data = [tuple(data) for data in df[columns].values]
        self.wdgts_table[-1].setRowCount(len(data))
        self.wdgts_table[-1].setColumnCount(len(columns))
        self.wdgts_table[-1].setHorizontalHeaderLabels(columns)
        for i in range(len(data)):
            for j in range(len(columns)):
                # set item to table
                self.wdgts_table[-1].setItem(i,j, QTableWidgetItem(data[i][j]))
        self.wdgts_table[-1].cellChanged.connect(self.cell_change)

    def createOutputCsvButton(self, text="OutputCsv"):
        # Create botton
        self.wdgt_output_csv_button = QPushButton(text, self)
        self.wdgt_output_csv_button.clicked.connect(self.output_csv)

    @pyqtSlot()
    def cell_change(self):
        # get signal
        sender = self.sender()
        target_column = sender.horizontalHeaderItem(1).text()
        row = sender.currentItem().row()
        column = sender.currentItem().column()
        text = sender.currentItem().text()
        self.output_df.iloc[row, column] = text
        
    def update_table(self, function, reference_df):
        self.function = function

        # clear twdgts_table to update
        self.wdgts_table.clear()

        # get args from list form string
        target_vars = reference_df[self.target_column].values[0].lstrip("[").rstrip("]").replace("'","").split(",")
        self.output_df = self.input_df[self.input_df[self.target_column].isin(target_vars)].copy()

        # create new table
        self.createTable(self.output_df, self.target_columns)

        # update layout
        self.updateLayout()
        self.update()

    @pyqtSlot()
    def output_csv(self):
        output_csv_root = os.path.join(os.path.join(self.output_root, self.function), "output_csv")
        os.makedirs(output_csv_root, exist_ok=True)
        self.output_df.to_csv(os.path.join(output_csv_root, self.output_csv_file_name), index=False)

    @pyqtSlot()
    def set_csv_file_name(self):
        # get signalaa
        sender = self.sender()
        self.output_csv_file_name = sender.displayText()
