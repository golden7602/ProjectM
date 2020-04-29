# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\Zion\zion\Ui\FormReport_Day.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1106, 798)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        Form.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.cbo_year = QtWidgets.QComboBox(Form)
        self.cbo_year.setMinimumSize(QtCore.QSize(100, 0))
        self.cbo_year.setAutoFillBackground(False)
        self.cbo_year.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.cbo_year.setModelColumn(0)
        self.cbo_year.setObjectName("cbo_year")
        self.horizontalLayout_3.addWidget(self.cbo_year)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.cbo_base = QtWidgets.QComboBox(Form)
        self.cbo_base.setMinimumSize(QtCore.QSize(100, 0))
        self.cbo_base.setObjectName("cbo_base")
        self.horizontalLayout_3.addWidget(self.cbo_base)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.CmdPrint = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CmdPrint.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../res/ico/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CmdPrint.setIcon(icon)
        self.CmdPrint.setIconSize(QtCore.QSize(16, 16))
        self.CmdPrint.setObjectName("CmdPrint")
        self.horizontalLayout_3.addWidget(self.CmdPrint)
        self.CmdPDF = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CmdPDF.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../res/ico/pdf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CmdPDF.setIcon(icon1)
        self.CmdPDF.setIconSize(QtCore.QSize(16, 16))
        self.CmdPDF.setObjectName("CmdPDF")
        self.horizontalLayout_3.addWidget(self.CmdPDF)
        self.CmdExportToExcel = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CmdExportToExcel.setFont(font)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../res/ico/export.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CmdExportToExcel.setIcon(icon2)
        self.CmdExportToExcel.setIconSize(QtCore.QSize(16, 16))
        self.CmdExportToExcel.setObjectName("CmdExportToExcel")
        self.horizontalLayout_3.addWidget(self.CmdExportToExcel)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setMinimumSize(QtCore.QSize(0, 250))
        self.tableView.setObjectName("tableView")
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(23)
        self.tableView.verticalHeader().setMinimumSectionSize(23)
        self.verticalLayout.addWidget(self.tableView)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Order"))
        self.label.setText(_translate("Form", "年度Year:"))
        self.label_3.setText(_translate("Form", "基于BasedOn:"))
        self.CmdPrint.setText(_translate("Form", "Print"))
        self.CmdPDF.setText(_translate("Form", "PDF"))
        self.CmdExportToExcel.setText(_translate("Form", "ExportToExcel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
