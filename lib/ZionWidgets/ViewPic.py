from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from Ui.Ui_FormViewPic import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from lib.JPPublc import JPPub
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class Form_ViewPic(QDialog):
    def __init__(self, parent=None, fn='', flags=Qt.WindowFlags()):
        pub = JPPub()
        super().__init__(parent=pub.MainForm, flags=flags)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.fn = fn
        self.dispPixmap = None
        self.ui.label.setScaledContents(False)
        self.showMaximized()

    def resizeEvent(self, resizeEvent):
        try:
            self.dispPixmap = JPPub().MainForm.getTaxCerPixmap(self.fn)
        except FileExistsError as e:
            self.ui.label.setText(e.Msg)
        if self.dispPixmap:
            size = self.ui.label.size()
            Pixmap = self.dispPixmap.scaled(size, Qt.KeepAspectRatio)
            self.ui.label.setPixmap(Pixmap)
