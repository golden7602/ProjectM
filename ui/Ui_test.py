# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ProjectM\Ui\test.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtCore import QCoreApplication, Qt, QVariant
from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtSql
from lib.JPPublc import JPDb, JPPub, JPUser



class myJPTableViewModelReadOnly(QtSql.QSqlRelationalTableModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ok_icon = QtGui.QIcon(
            r'E:\ProjectM\res\ico\yes.ico')

    def data(self, index, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        if c in (7, 8, 9):
            if role == Qt.DisplayRole:
                return ''
            if role == Qt.TextAlignmentRole:
                return (Qt.AlignLeft | Qt.AlignVCenter)
            if role == Qt.DecorationRole:
                # if self.TabelFieldInfo.getOnlyData((r, c)):
                return self.ok_icon
            else:
                return super().data(index, role=role)
        else:
            return super().data(index, role=role)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1057, 722)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setObjectName("tableView")
        self.verticalLayout_3.addWidget(self.tableView)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_3.addWidget(self.pushButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.pushButton.clicked.connect(self.dispData)
        JPDb().getQSqlDatabase()
        self.Model = QtSql.QSqlRelationalTableModel()
        self.Model.setTable('ttt')
        # Relation = QtSql.QSqlRelation("t_enumeration", "fItemID", "fTitle")
        # self.Model.setRelation(3, Relation)
        #Model.setFilter("False")
        self.Model.setSort(1, Qt.DescendingOrder)
        # header = ['文档编号',
        #           '发文日期',
        #           '文号',
        #           '文件类型',
        #           '文件标题',
        #           '发文单位',
        #           '关键字',
        #           '是否手续文件',
        #           '是否任务来源',
        #           '是否进度文件',
        #           '涉及项目数',
        #           '涉及项目']
        # for i, r in enumerate(header):
        #     self.Model.setHeaderData(i, Qt.Horizontal, r)
        
        self.tableView.setModel(self.Model)
        

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "PushButton"))

    def dispData(self):
        self.Model.select()
        self.tableView.resizeColumnsToContents()
        re = self.Model.record()
        for i in range(re.count()):
            fld=re.field(i)
            print("MySql typeName="+fld.name().ljust(20), "mySql typeID="+str(fld.typeID()
                                                                              ).rjust(3), ",      Qt TypeName="+QVariant.typeToName(fld.type()).ljust(10),"Qt type="+str(fld.type()).rjust(2))
        # db = QtSql.QSqlDatabase.addDatabase("QMYSQL3")
        # db.setHostName("192.168.1.20")
        # db.setPort(3306)
        # db.setDatabaseName("project_m")
        # db.setUserName('jhglb')
        # db.setPassword('1234')
        # QtSql.QSqlQuery()
        # db.query('select * from t_archives limit 1')
        # if db.open():
        #     print("ok")
        # else:
        #     print("Error")



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    sys.exit(app.exec_())
