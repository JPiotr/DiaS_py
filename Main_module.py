import sys
from PyQt5 import QtCore, QtWidgets, Qt, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # properties

        # methods
        self.init_ui()
        pass

    def init_ui(self):
        self.setWindowTitle("DiaS")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
