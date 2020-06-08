# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ProjectM\Ui\FormToolsImport.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1124, 606)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_import = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_import.sizePolicy().hasHeightForWidth())
        self.label_import.setSizePolicy(sizePolicy)
        self.label_import.setText("")
        self.label_import.setPixmap(QtGui.QPixmap("../res/ico/import1.png"))
        self.label_import.setObjectName("label_import")
        self.horizontalLayout_5.addWidget(self.label_import)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox_FileType = QtWidgets.QComboBox(Form)
        self.comboBox_FileType.setObjectName("comboBox_FileType")
        self.verticalLayout.addWidget(self.comboBox_FileType)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.butPathImport = QtWidgets.QPushButton(Form)
        self.butPathImport.setMinimumSize(QtCore.QSize(0, 48))
        self.butPathImport.setMaximumSize(QtCore.QSize(80, 48))
        self.butPathImport.setObjectName("butPathImport")
        self.horizontalLayout_5.addWidget(self.butPathImport)
        self.butFileImport = QtWidgets.QPushButton(Form)
        self.butFileImport.setMinimumSize(QtCore.QSize(0, 48))
        self.butFileImport.setMaximumSize(QtCore.QSize(80, 48))
        self.butFileImport.setObjectName("butFileImport")
        self.horizontalLayout_5.addWidget(self.butFileImport)
        self.horizontalLayout.addLayout(self.horizontalLayout_5)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_info = QtWidgets.QLabel(Form)
        self.label_info.setMinimumSize(QtCore.QSize(500, 0))
        self.label_info.setObjectName("label_info")
        self.horizontalLayout_3.addWidget(self.label_info)
        self.pb = QtWidgets.QProgressBar(Form)
        self.pb.setMinimumSize(QtCore.QSize(200, 0))
        self.pb.setMaximumSize(QtCore.QSize(200, 16777215))
        self.pb.setProperty("value", 24)
        self.pb.setObjectName("pb")
        self.horizontalLayout_3.addWidget(self.pb)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "选择要导入的文档类型"))
        self.butPathImport.setText(_translate("Form", "导入子文件夹"))
        self.butFileImport.setText(_translate("Form", "导入文件"))
        self.label_info.setText(_translate("Form", "TextLabel"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
