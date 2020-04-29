from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from Ui.Ui_FormBackup import Ui_Dialog
from configparser import ConfigParser
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPPublc import JPPub
from lib.JPDatabase.ExportSQL import CreateSQL_MySQL


class Form_Backup(QDialog):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.MainForm = JPPub().MainForm
        self.setWindowTitle("数据备份Backup")
        self.ui.butBegin.clicked.connect(self.__run)
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

    def __run(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(
            JPPub().MainForm,
            "Export To SQL File Name",
            getcwd(),  # 起始路径
            "Excel Files (*.sql)")
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
        QMessageBox.information(self, "提示", "导数据完成！")
        self.close()
