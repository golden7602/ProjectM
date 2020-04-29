# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\Zion\zion\Ui\FormProductSelecer.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProductSelecer(object):
    def setupUi(self, ProductSelecer):
        ProductSelecer.setObjectName("ProductSelecer")
        ProductSelecer.resize(1025, 356)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        ProductSelecer.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProductSelecer)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(ProductSelecer)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(ProductSelecer)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 25))
        self.lineEdit.setMaximumSize(QtCore.QSize(200, 25))
        self.lineEdit.setSizeIncrement(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtWidgets.QTableView(ProductSelecer)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.tableView.verticalHeader().setDefaultSectionSize(25)
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(ProductSelecer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ProductSelecer)
        self.buttonBox.accepted.connect(ProductSelecer.accept)
        self.buttonBox.rejected.connect(ProductSelecer.reject)
        QtCore.QMetaObject.connectSlotsByName(ProductSelecer)

    def retranslateUi(self, ProductSelecer):
        _translate = QtCore.QCoreApplication.translate
        ProductSelecer.setWindowTitle(_translate("ProductSelecer", "ProductSelecer"))
        self.label.setText(_translate("ProductSelecer", "商品名称Product Name："))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ProductSelecer = QtWidgets.QDialog()
    ui = Ui_ProductSelecer()
    ui.setupUi(ProductSelecer)
    ProductSelecer.show()
    sys.exit(app.exec_())
