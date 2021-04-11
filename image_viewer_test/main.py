import argparse
import sys
from pyqt5_image_viewer_test import PyQt5ImageViewerTest
from PyQt5.QtWidgets import QApplication

def parse_arguments():
    parser = argparse.ArgumentParser(description='Please specify some options.')
    parser.add_argument('-cw', '--canvas_width', type=int, default=420, help='canvas_width')
    parser.add_argument('-ch', '--canvas_height', type=int, default=300, help='canvas_height')

    return parser.parse_args()

def main():
    options = parse_arguments()
    qapp = QApplication(sys.argv)
    pyqt5_test_obj = PyQt5ImageViewerTest(options.canvas_width, options.canvas_height)
    sys.exit(qapp.exec_())

if __name__ == '__main__':
    main()