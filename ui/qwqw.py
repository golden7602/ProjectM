
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import os



class MyWindow(QDialog):

    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.widget1 = QListWidget()
        self.widget1.setWindowTitle('aaaaaa')
        self.layout.addWidget(self.widget1)
        self.widget1.resize(300, 200)
        self.widget2 = QListWidget()
        self.widget2.setWindowTitle('bbbbbb')
        self.widget2.resize(300, 200)
        self.layout.addWidget(self.widget2)
        self._diyWindow = DiyWindow()
        self.layout.addWidget(self._diyWindow)
        self.setLayout(self.layout)
        #self.resize(300,200)


class DiyWindow(QDialog):
    def __init__(self, parent=None):
        super(DiyWindow, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.widget = QListWidget()
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)
        self.widget.resize(300, 200)
    # 当按右键的时候，这个event会被触发
    def contextMenuEvent(self, event):

        menu = QMenu(self)
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
