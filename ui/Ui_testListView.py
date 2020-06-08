# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ProjectM\Ui\testListView.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets,Qt


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1032, 783)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 1011, 761))
        
        self.listWidget.setViewMode(QtWidgets.QListView.IconMode)
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate

        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))




if __name__ == "__main__":
    import sys
    import os
    path=os.path.join(os.getcwd(),"cache")
    fns=os.listdir(path)
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    #sz = QtCore.QSize(105, 155)

    def itemDoubleClicked(pItem):
        print(pItem.data)
    ui.listWidget.setGridSize(QtCore.QSize(210, 330))
    ui.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
    ui.listWidget.setIconSize(QtCore.QSize(210, 330))
    ui.listWidget.setSpacing(10)
    ui.listWidget.itemDoubleClicked.connect(itemDoubleClicked)

    for i, fn  in enumerate(fns):
        obj = QtGui.QPixmap(os.path.join(path, fn))
        pItem = QtWidgets.QListWidgetItem(QtGui.QIcon(obj.scaled(  
            QtCore.QSize(210, 330), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)),'')
        pItem.setSizeHint(QtCore.QSize(210, 330))
        pItem.data=['aa','bb']
        ui.listWidget.insertItem(i,pItem)
        QtGui.QGuiApplication.processEvents()

    sys.exit(app.exec_())
