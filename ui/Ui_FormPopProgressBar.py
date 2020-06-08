# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ProjectM\Ui\FormPopProgressBar.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, Qt


class FormPopProgressBar(QtWidgets.QDialog):
    def __init__(self, parent=None, flags=Qt.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.setObjectName("Dialog")
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        h = 105
        w = 560
        self.resize(w, h)
        self.setMinimumSize(QtCore.QSize(w, h))
        self.setMaximumSize(QtCore.QSize(w, h))
        LABEL = QtWidgets.QLabel(self)
        self.LABEL = LABEL
        LABEL.setGeometry(QtCore.QRect(30, 0, 511, 41))
        LABEL.setObjectName("label")
        LABEL.setText("")
        PB = QtWidgets.QProgressBar(self)
        self.PB = PB
        PB.setGeometry(QtCore.QRect(20, 60, 520, 23))
        PB.setProperty("value", 24)
        PB.setTextVisible(False)
        PB.setFormat("")
        PB.setObjectName("progressBar")
        PB.value = 0
        PB.minimum = 0
        PB.maximum = 0

    def showInfo(self, maxValue=0):
        self.PB.maximum = maxValue
        self.LABEL.setText('')
        self.exec_()

    def dispInfo(self, text='', value=0):
        self.PB.value = value
        self.LABEL.setText(text)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = FormPopProgressBar()

    Dialog.showInfo()
    sys.exit(app.exec_())
