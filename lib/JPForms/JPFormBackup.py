from lib.JPDatabase.ExportSQL import CreateSQL_MySQL
from lib.JPPublc import JPPub
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPDatabase.Database import JPDb
from configparser import ConfigParser
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(447, 127)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_2.addWidget(self.progressBar)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 11, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.butBegin = QtWidgets.QPushButton(Dialog)
        self.butBegin.setObjectName("butBegin")
        self.horizontalLayout.addWidget(self.butBegin)
        spacerItem5 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem6 = QtWidgets.QSpacerItem(
            20, 7, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        Dialog.setToolTip(_translate(
            "Dialog", "<html><head/><body><p><br/></p></body></html>"))
        self.butBegin.setText(_translate("Dialog", "Begin"))


class Form_Backup(QtWidgets.QDialog):
    def __init__(self, savePath='', parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.savePath = savePath
        self.MainForm = JPPub().MainForm
        self.setWindowTitle("数据备份Backup")
        self.ui.butBegin.clicked.connect(self._run)
        self.ui.progressBar.setValue(0)

        self.exec_()

    def refreshProgressBar(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)

    def __getCr(self, d, n, isView=False):
        if isView:
            sql = 'SHOW CREATE VIEW `{}`.`{}`'.format(d, n)
        else:
            sql = 'SHOW CREATE TABLE `{}`.`{}`'.format(d, n)
        tab = JPQueryFieldInfo(sql)
        return tab.DataRows[0].Datas[1] + '\n'

    def _run(self):
        if not self.savePath:
            fileName_choose, filetype = QtWidgets.QFileDialog.getSaveFileName(
                JPPub().MainForm,
                "Export To SQL File Name",
                getcwd(),  # 起始路径
                "SQL Files (*.sql)")
        else:
            fileName_choose = self.savePath
        if not fileName_choose:
            return
        file_ = open(fileName_choose, 'w', encoding='utf-8')
        # 取所有表名
        config = ConfigParser()
        config.read("config.ini", encoding="utf-8")
        dbn = dict(config._sections["database"])["database"]
        bases_sql = "SHOW TABLE STATUS FROM `{}`".format(dbn)
        tab = JPDb().getDict(bases_sql)
        tns = [r['Name'] for r in tab if r['Engine']]
        tns = [r for r in tns if not r in ['syssql', 'syslanguage']]
        views = [r['Name'] for r in tab if r['Comment'] == 'VIEW']
        recs = 0
        for r in tab:
            recs += r['Rows'] if r['Rows'] else 0
        self.ui.progressBar.setRange(0, recs)
        exp = CreateSQL_MySQL()
        exp.exportOneRecord.connect(self.refreshProgressBar)
        for tn in tns:
            file_.write('-- 导出  表 {}.{} 结构'.format(dbn, tn))
            file_.write('\n')
            file_.write('DROP TABLE IF EXISTS `{}`;'.format(tn))
            file_.write('\n')
            file_.write(self.__getCr(dbn, tn, False) + ";")
            file_.write('\n')
            tempSQL = exp.getSql(tn)
            if tempSQL:
                file_.write(tempSQL)
            file_.write('\n')
        for vn in views:
            file_.write('-- 导出  视图 {}.{} 结构'.format(dbn, vn))
            file_.write('\n')
            file_.write('DROP View IF EXISTS `{}`;'.format(vn))
            file_.write('\n')
            file_.write(self.__getCr(dbn, vn, True) + ";")
            file_.write('\n')
        self.ui.progressBar.hide()

        file_.close()
        QtWidgets.QMessageBox.information(self, "提示", "导数据完成！")
        self.close()
