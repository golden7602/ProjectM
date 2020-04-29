# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\Zion\Ui\FormSearch.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DlgSearch(object):
    def setupUi(self, DlgSearch):
        DlgSearch.setObjectName("DlgSearch")
        DlgSearch.resize(702, 349)
        DlgSearch.setMinimumSize(QtCore.QSize(0, 0))
        DlgSearch.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        DlgSearch.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(DlgSearch)
        self.verticalLayout.setContentsMargins(3, 3, 3, 10)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(DlgSearch)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(DlgSearch)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgSearch)
        self.buttonBox.accepted.connect(DlgSearch.accept)
        self.buttonBox.rejected.connect(DlgSearch.reject)
        QtCore.QMetaObject.connectSlotsByName(DlgSearch)

    def retranslateUi(self, DlgSearch):
        _translate = QtCore.QCoreApplication.translate
        DlgSearch.setWindowTitle(_translate("DlgSearch", "Search"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DlgSearch = QtWidgets.QDialog()
    ui = Ui_DlgSearch()
    ui.setupUi(DlgSearch)
    DlgSearch.show()
    sys.exit(app.exec_())

