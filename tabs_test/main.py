import argparse
import sys
from pyqt5_tabs_test import PyQt5TabsTest
from PyQt5.QtWidgets import QApplication

def parse_arguments():
    parser = argparse.ArgumentParser(description='Please specify some options.')
    parser.add_argument('-func', '--func_info', type=str, default='./func_info.csv', help='function information file(columns=[type,function,args,gl_vars])')
    parser.add_argument('-args', '--args_info', type=str, default='./args_info.csv', help='function information file(columns=[type,args])')
    parser.add_argument('-gl_vars', '--gl_vars_info', type=str, default='./gl_vars_info.csv', help='function information file(columns=[type,gl_vars])')

    return parser.parse_args()

def main():
    options = parse_arguments()
    qapp = QApplication(sys.argv)
    pyqt5_test_obj = PyQt5TabsTest(options.func_info, options.args_info, options.gl_vars_info)
    sys.exit(qapp.exec_())

if __name__ == '__main__':
    main()
