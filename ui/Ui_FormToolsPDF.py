# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ProjectM\Ui\FormToolsPDF.ui'
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
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_pdf = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_pdf.sizePolicy().hasHeightForWidth())
        self.label_pdf.setSizePolicy(sizePolicy)
        self.label_pdf.setText("")
        self.label_pdf.setPixmap(QtGui.QPixmap("../res/ico/file_pdf.png"))
        self.label_pdf.setObjectName("label_pdf")
        self.horizontalLayout_6.addWidget(self.label_pdf)
        self.butPic2PDF = QtWidgets.QPushButton(Form)
        self.butPic2PDF.setMinimumSize(QtCore.QSize(0, 48))
        self.butPic2PDF.setMaximumSize(QtCore.QSize(80, 48))
        self.butPic2PDF.setObjectName("butPic2PDF")
        self.horizontalLayout_6.addWidget(self.butPic2PDF)
        self.butSplitPDF = QtWidgets.QPushButton(Form)
        self.butSplitPDF.setMinimumSize(QtCore.QSize(0, 48))
        self.butSplitPDF.setMaximumSize(QtCore.QSize(80, 48))
        self.butSplitPDF.setObjectName("butSplitPDF")
        self.horizontalLayout_6.addWidget(self.butSplitPDF)
        self.butMergePDF = QtWidgets.QPushButton(Form)
        self.butMergePDF.setMinimumSize(QtCore.QSize(0, 48))
        self.butMergePDF.setMaximumSize(QtCore.QSize(80, 48))
        self.butMergePDF.setObjectName("butMergePDF")
        self.horizontalLayout_6.addWidget(self.butMergePDF)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.horizontalLayout_6)
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
        self.butPic2PDF.setText(_translate("Form", "图片转PDF"))
        self.butSplitPDF.setText(_translate("Form", "拆分PDF"))
        self.butMergePDF.setText(_translate("Form", "合并PDF"))
        self.label_info.setText(_translate("Form", "TextLabel"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
