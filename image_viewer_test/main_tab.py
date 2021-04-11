import pandas as pd
import numpy as np
import cv2
import math
import os
import pytesseract
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from time import sleep

class MainTab(QWidget):
    def __init__(self, canvas_width, canvas_height):
        super().__init__()

        # setting ui parameters
        self.layout = QVBoxLayout()
        
        # define widgets
        self.wdgt_input_label = None
        self.wdgt_input_edit = None
        self.wdgt_output_label = None
        self.wdgt_output_edit = None
        self.wdgt_viewer_label = None
        self.wdgt_start_button = None
        self.wdgt_stop_button = None
        self.wdgt_load_button = None
        self.wdgt_combobox = None
        self.wdgt_slider = None
        self.wdgt_table = None
        self.wdgt_save_button = None
        self.wdgt_quit_button = None
        
        # to output code
        self.input_file_name = ""
        self.output_file_name = ""

        # image, video
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.curr_mode = "RGB"
        self.img = None
        self.cap = None
        self.load_type = 0 # 0:None, 1:img, 2:cap
        self.fps = -1
        self.total_frame = -1
        self.min_pos = -1
        self.max_pos = -1
        self.curr_pos = -1
        self.cap_state = 0 # 0:stop, 1:running
        self.time_interval = 500 # [ms]
        self.ocr_data = []

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_passes)
        
        # create widgets
        self.create_input_file_label("input_file_name(*.png, *.mp4, *.mkv):")
        self.create_input_line_edit()
        self.create_output_file_label("output_file_name(*.png):")
        self.create_output_line_edit()
        self.create_canvas()
        self.create_combo_box()
        self.create_slider()
        self.create_table()
        self.create_start_button()
        self.create_stop_button()
        self.create_load_button()
        self.create_save_button()
        self.create_quit_button()

        # create layout
        self.update_layout()

    def update_layout(self):
        # remove all widgets
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        # add list to layout
        self.layout.addWidget(self.wdgt_input_label)
        self.layout.addWidget(self.wdgt_input_edit)
        self.layout.addWidget(self.wdgt_output_label)
        self.layout.addWidget(self.wdgt_output_edit)
        self.layout.addWidget(self.wdgt_viewer_label)
        self.layout.addWidget(self.wdgt_table)
        self.layout.addWidget(self.wdgt_combobox)
        if self.load_type == 2:
            self.wdgt_slider.setMinimum(self.min_pos)
            self.wdgt_slider.setMaximum(self.max_pos)
            self.wdgt_slider.setValue(self.curr_pos)
            self.wdgt_slider.setTickInterval(1)
            self.layout.addWidget(self.wdgt_slider)
            self.layout.addWidget(self.wdgt_start_button)
            self.layout.addWidget(self.wdgt_stop_button)
        self.layout.addWidget(self.wdgt_load_button)
        self.layout.addWidget(self.wdgt_save_button)
        self.layout.addWidget(self.wdgt_quit_button) 
        self.setLayout(self.layout)

    def create_input_file_label(self, text):
        self.wdgt_input_label = QLabel(text)

    def create_output_file_label(self, text):
        self.wdgt_output_label = QLabel(text)

    def createSlidePosLabel(self, text):
        self.wdgt_slide_pos_label = QLabel(text)
        
    def create_input_line_edit(self):
        self.wdgt_input_edit = QLineEdit()
        self.wdgt_input_edit.textChanged.connect(self.set_input_file_name)
        
    def create_output_line_edit(self):
        self.wdgt_output_edit = QLineEdit()
        self.wdgt_output_edit.textChanged.connect(self.set_output_file_name)

    def create_canvas(self):
        self.load_type = 0
        self.img = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        self.img.fill(255)
        temp_img = np.zeros((0, 0, 0))
        if os.path.isfile(self.input_file_name):
            if os.path.splitext(self.input_file_name)[1] == ".png":
                temp_img = cv2.imread(self.input_file_name)
                if self.curr_mode == "RGB":
                    temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)
                elif self.curr_mode == "MONO":
                    temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
                    temp_img = np.stack((temp_img,) * 3, -1)
                    ret, temp_img = cv2.threshold(temp_img, 100, 255, cv2.THRESH_BINARY)
                self.load_type = 1
            elif os.path.splitext(self.input_file_name)[1] in [".mp4", ".mkv"]:
                self.cap = cv2.VideoCapture(self.input_file_name)
                if self.cap.isOpened():
                    ret, temp_img = self.cap.read()
                    if self.curr_mode == "RGB":
                        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB) 
                    elif self.curr_mode == "MONO":
                        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
                        temp_img = np.stack((temp_img,) * 3, -1)
                        ret, temp_img = cv2.threshold(temp_img, 100, 255, cv2.THRESH_BINARY)
                    self.load_type = 2
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                    self.total_frame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    self.min_pos = 0
                    self.max_pos = self.total_frame - 1
                    self.curr_pos = 0
                    self.cap.release()
        if np.sum(temp_img.shape) != 0:
            h, w = temp_img.shape[:2]
            resize_rate = min(self.canvas_width/w, self.canvas_height/h)
            rh, rw = int(h*resize_rate), int(w*resize_rate)
            rimg = cv2.resize(temp_img, (rw, rh))
            self.img[0:rh,0:rw] = rimg
        self.ocr_data = pytesseract.image_to_string(self.img).split("\n")
        self.img = cv2.rectangle(self.img, (0,0),(self.canvas_width-1,self.canvas_height-1),(0,0,0),1,1)
        qimg = QImage(self.img.flatten(), self.canvas_width, self.canvas_height, QImage.Format_RGB888)
        self.wdgt_viewer_label = QLabel()
        self.wdgt_viewer_label.setPixmap(QPixmap.fromImage(qimg))
        self.wdgt_viewer_label.scaleFactor = 1.0

    def update_canvas_label(self):
        self.load_type = 0
        self.img = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        self.img.fill(255)
        temp_img = np.zeros((0, 0, 0))
        if os.path.isfile(self.input_file_name):
            if os.path.splitext(self.input_file_name)[1] in [".mp4", ".mkv"]:
                self.cap = cv2.VideoCapture(self.input_file_name)
                if self.cap.isOpened():
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                    self.total_frame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.curr_pos))
                    ret, temp_img = self.cap.read()
                    if self.curr_mode == "RGB":
                        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)
                    elif self.curr_mode == "MONO":
                        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
                        temp_img = np.stack((temp_img,) * 3, -1)
                        ret, temp_img = cv2.threshold(temp_img, 100, 255, cv2.THRESH_BINARY)
                    self.load_type = 2
                    self.min_pos = 0
                    self.max_pos = self.total_frame - 1
                    self.cap.release()
        if np.sum(temp_img.shape) != 0:
            h, w = temp_img.shape[:2]
            resize_rate = min(self.canvas_width/w, self.canvas_height/h)
            rh, rw = int(h*resize_rate), int(w*resize_rate)
            rimg = cv2.resize(temp_img, (rw, rh))
            self.img[0:rh,0:rw] = rimg
        self.ocr_data = pytesseract.image_to_string(self.img).split("\n")
        self.img = cv2.rectangle(self.img, (0,0),(self.canvas_width-1,self.canvas_height-1),(0,0,0),1,1)
        qimg = QImage(self.img.flatten(), self.canvas_width, self.canvas_height, QImage.Format_RGB888)
        self.wdgt_viewer_label = QLabel()
        self.wdgt_viewer_label.setPixmap(QPixmap.fromImage(qimg))
        self.wdgt_viewer_label.scaleFactor = 1.0

    def create_combo_box(self):
        self.wdgt_combobox = QComboBox()
        self.wdgt_combobox.addItem("RGB")
        self.wdgt_combobox.addItem("MONO")
        self.wdgt_combobox.currentTextChanged.connect(self.change_mode)

    def create_slider(self):
        self.wdgt_slider = QSlider(Qt.Horizontal)
        self.wdgt_slider.setFocusPolicy(Qt.NoFocus)
        self.wdgt_slider.valueChanged.connect(self.slide_pos)
        self.wdgt_slider.sliderReleased.connect(self.release_slide)

    def create_table(self, src=[]):
        self.wdgt_table = QTableWidget()
        self.wdgt_table.setColumnCount(1)
        self.wdgt_table.setHorizontalHeaderLabels(["pytesseract"])
        data = [datum for datum in src if len(datum) != 0]
        self.wdgt_table.setRowCount(len(data))
        for i, datum in enumerate(data):
            self.wdgt_table.setItem(i, 0, QTableWidgetItem(str(datum)))
        self.wdgt_table.resizeRowsToContents()
        self.wdgt_table.resizeColumnsToContents()

    def create_start_button(self, text="Start"):
        self.wdgt_start_button = QPushButton(text)
        self.wdgt_start_button.clicked.connect(self.cap_start)

    def create_stop_button(self, text="Stop"):
        self.wdgt_stop_button = QPushButton(text)
        self.wdgt_stop_button.clicked.connect(self.cap_stop)

    def create_load_button(self, text="Load"):
        self.wdgt_load_button = QPushButton(text)
        self.wdgt_load_button.clicked.connect(self.load_img)

    def create_save_button(self, text="Save"):
        self.wdgt_save_button = QPushButton(text)
        self.wdgt_save_button.clicked.connect(self.save_img)

    def create_quit_button(self, text="Quit"):
        self.wdgt_quit_button = QPushButton(text)
        self.wdgt_quit_button.clicked.connect(QCoreApplication.instance().quit)

    @pyqtSlot()
    def slide_pos(self):
        self.curr_pos = self.wdgt_slider.value()
    
    @pyqtSlot()
    def time_passes(self):
        if self.cap_state == 1:
            self.curr_pos += math.ceil(self.fps / 1000 * self.time_interval)
            if self.curr_pos > self.max_pos:
                self.curr_pos = self.min_pos
            self.update_canvas_label()
            self.create_table(self.ocr_data)
            self.update_layout()
    
    @pyqtSlot()
    def change_mode(self):
        self.curr_mode = self.wdgt_combobox.currentText()

    @pyqtSlot()
    def release_slide(self):
        self.update_canvas_label()
        self.create_table(self.ocr_data)
        self.update_layout()

    @pyqtSlot()
    def set_input_file_name(self):
        self.input_file_name = self.wdgt_input_edit.displayText()
    
    @pyqtSlot()
    def set_output_file_name(self):
        self.output_file_name = self.wdgt_output_edit.displayText()
    
    @pyqtSlot()
    def cap_start(self):
        self.timer.start(self.time_interval)
        self.cap_state = 1
    
    @pyqtSlot()
    def cap_stop(self):
        self.timer.stop()
        self.cap_state = 0

    @pyqtSlot()
    def load_img(self):
        self.create_canvas()
        self.create_table(self.ocr_data)
        self.update_layout()

    @pyqtSlot()
    def save_img(self):
        dir_name = os.path.dirname(self.output_file_name)
        if len(dir_name) != 0:
            os.makedirs(dir_name, exist_ok=True)
        if os.path.splitext(self.output_file_name)[1] == ".png":
            cv2.imwrite(self.output_file_name, cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR))