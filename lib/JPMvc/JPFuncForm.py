import datetime
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from dateutil.relativedelta import relativedelta
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox,
                             QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
                             QTableView, QVBoxLayout, QWidget, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import (QCoreApplication, QSize, Qt, pyqtSlot, QModelIndex,
                          pyqtSignal)
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode
from lib.JPDatabase.Database import JPDb
from Ui.Ui_FuncFormMob import Ui_Form
from lib.JPExcel.JPExportToExcel import clsExportToExcelFromTableWidget
import re
import abc
from lib.JPForms.JPSearch import Form_Search


class JPFunctionForm(QWidget):
    currentRowChanged = pyqtSignal(QModelIndex, QModelIndex)
    afterCreateEditForm = pyqtSignal(int)

    def __init__(self, parent, flags=Qt.WindowFlags()):
        super().__init__(parent, flags=flags)
        # 把本窗体加入主窗体
        parent.addForm(self)
        self.MainForm = parent
        self.TableInfo = None
        self.SQL_ListForm_Para = ''
        self.SQL_ListForm_Base = ''
        self.backgroundWhenValueIsTrueFieldName = []
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        #parent.addButtons()
        self.comboBox = self.ui.comboBox
        self.checkBox_1 = self.ui.checkBox_1
        self.checkBox_2 = self.ui.checkBox_2
        self.tableView = self.ui.tableView
        self.__FormClass = None
        self.PrimarykeyFieldIndex = 0
        self.__EditForm = None
        self.EditFormMainTableName = None
        self.EditFormPrimarykeyFieldName = None
        self.EditFormSubTableName = None

        # 以下为初始化部分
        self.ui.comboBox.addItems(['Today', 'Last Month', 'Last Year', 'All'])
        self.ui.comboBox.setCurrentIndex(0)
        self.ui.checkBox_1.clicked.connect(self.refreshListForm)
        self.ui.checkBox_2.clicked.connect(self.refreshListForm)
        self.ui.comboBox.activated['int'].connect(self.refreshListForm)
        # 行交错颜色
        self.ui.tableView.setAlternatingRowColors(True)
        self.SQL_EditForm_Main = None
        self.SQL_EditForm_Sub = None

    def setListFormSQL(self, sql_with_where, sql_base):
        '''
        setSQL(sql_without_para, where_string)\n
        sql_without_para: 不带Where子句的sql
        where_string： where子句，参数用{}表示
        '''
        self.SQL_ListForm_Para = sql_with_where
        self.SQL_ListForm_Base = sql_base
        self.refreshListForm()

    def __getTableNameInfo(self, sql, errType=1):
        # 返回一个指定SQL语句的表名和条件字段名
        sql = re.sub(r'^\s', '', re.sub(r'\s+', ' ', re.sub(r'\n', '', sql)))
        sel_p = r"SELECT\s+.*from\s(\S+)\s(as\s\S+){0,1}where\s(\S+)\s*=.*"
        mt = re.match(sel_p, sql, flags=(re.I))
        if mt:
            return mt.groups()[0], mt.groups()[2]
        else:
            errStr = "主窗体" if errType == 1 else "子窗体"
            errStr = errStr + 'SQL语句格式有误,必须类似以下格式：\n'
            errStr = errStr + "SELECT fieldsList from tab where fld={}\n"
            errStr = errStr + '而当前设定语句为:\n'
            errStr = errStr + sql
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', errStr)
            msgBox.exec_()

    def _onGetEditFormSQL(self):
        sql_main, sql_sub = self.onGetEditFormSQL()
        if sql_main:
            self.SQL_EditForm_Main = sql_main
            a, b = self.__getTableNameInfo(sql_main)
            self.EditFormMainTableName = a
            self.EditFormPrimarykeyFieldName = b
        else:
            raise ValueError("必须指定主窗体SQL语句")
        if sql_sub:
            self.SQL_EditForm_Sub = sql_sub
            self.EditFormSubTableName = self.__getTableNameInfo(sql_sub)

    def setEditFormSQL(self, sql_main, sql_sub):
        if sql_main:
            self.SQL_EditForm_Main = sql_main
            a, b = self.__getTableNameInfo(sql_main)
            self.EditFormMainTableName = a
            self.EditFormPrimarykeyFieldName = b
        else:
            raise ValueError("必须指定主窗体SQL语句")
        if sql_sub:
            self.SQL_EditForm_Sub = sql_sub
            self.EditFormSubTableName = self.__getTableNameInfo(sql_sub)

    def onGetEditFormSQL(self):
        """指定编辑窗体语句，返回两个参数，第一个是主表SQL，第二个是子表SQL，可省略"""
        return None, None

    def onGetModelClass(self):
        '''此类可以重写，改写列表Model的行为,必须返回一个模型类
        重写时可以在重载方法中内部定义模型类并继承自已有模型类，将该类返回
        '''
        return JPTableViewModelReadOnly

    @abc.abstractmethod
    def getEditForm(self,
                    sql_main=None,
                    edit_mode=None,
                    sql_sub=None,
                    PKValue=None):
        """重载此方法，返回一个编辑窗体对象"""
        raise ("没有重载getEditForm方法")

    def beforeDeleteRow(self, delete_ID):
        '''删除行之前查检用方法，可重载'''
        return True

    def refreshListForm(self, ID=None):
        # 记录按钮状态
        dict_but = {
            but: but.isEnabled()
            for but in self.findChildren((QPushButton))
        }
        for but in dict_but.keys():
            but.setEnabled(False)
        self.ui.checkBox_1.setEnabled(False)
        self.ui.checkBox_2.setEnabled(False)
        self.ui.comboBox.setEnabled(False)
        if self.SQL_ListForm_Para:
            self.ui.tableView.setSelectionMode(
                QAbstractItemView.SingleSelection)
            ch1 = 1 if self.ui.checkBox_1.isChecked() else 0
            ch2 = 0 if self.ui.checkBox_2.isChecked() else 1
            cb = {
                0:
                '=CURRENT_DATE()',
                1: (datetime.date.today() -
                    relativedelta(months=1)).strftime(">='%Y-%m-%d'"),
                2: (datetime.date.today() -
                    relativedelta(years=1)).strftime(">='%Y-%m-%d'"),
                3:
                '=fOrderDate'
            }
            sql = self.SQL_ListForm_Para.format(
                ch1=ch1, ch2=ch2, date=cb[self.ui.comboBox.currentIndex()])
            #print(sql)
            self.__readSQL(sql)
            if ID:
                self._locationRow(ID)

        # 恢复按钮状态
        for but in dict_but.keys():
            but.setEnabled(dict_but[but])
        self.ui.checkBox_1.setEnabled(True)
        self.ui.checkBox_2.setEnabled(True)
        self.ui.comboBox.setEnabled(True)

    def __readSQL(self, sql):
        info = JPQueryFieldInfo(sql)
        self.currentSQL = sql
        self.MainForm.ProgressBar.show()
        self.MainForm.Label.setText('Reading')
        self.model = self.onGetModelClass()(self.ui.tableView, info)
        self.model.readingRow.connect(self.__refreshProcessBar)
        self.MainForm.ProgressBar.setRange(0, len(info))
        self.ui.tableView.setModel(self.model)
        self.MainForm.Label.setText('')
        self.MainForm.ProgressBar.hide()
        self.ui.tableView.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(
            self.onCurrentRowChanged)
        self.ui.tableView.resizeColumnsToContents()
        self.TableInfo = info

    def __refreshProcessBar(self, row):
        try:
            self.MainForm.ProgressBar.setValue(row)
        except Exception:
            pass

    def onCurrentRowChanged(self, QModelIndex1, QModelIndex2):
        """当前行改变事件"""
        return

    def getCurrentSelectPKValue(self):
        index = self.tableView.selectionModel().currentIndex()
        if index.isValid():
            return self.model.TabelFieldInfo.getOnlyData(
                [index.row(), self.PrimarykeyFieldIndex])

    def getCurrentColumnValue(self, col):
        index = self.tableView.selectionModel().currentIndex()
        if index.isValid():
            return self.model.TabelFieldInfo.getOnlyData([index.row(), col])

    # 定位到某一行
    def _locationRow(self, id):
        tab = self.model.TabelFieldInfo
        c = self.PrimarykeyFieldIndex
        for r in range(len(tab.DataRows)):
            if tab.getOnlyData([r, c]) == id:
                index = self.model.createIndex(r, c)
                self.ui.tableView.setCurrentIndex(index)
                return

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        print("CmdExportToExcel方法未定义")
        return

    def __whereStringCreated(self, sql):
        self.__readSQL(sql)

    @pyqtSlot()
    def on_CmdSearch_clicked(self):
        frm = Form_Search(self.TableInfo, self.SQL_ListForm_Base)
        frm.whereStringCreated.connect(self.__whereStringCreated)
        frm.exec_()

    @pyqtSlot()
    def on_CmdNew_clicked(self):
        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=self.SQL_EditForm_Sub,
                               edit_mode=JPEditFormDataMode.New,
                               PKValue=None)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshListForm)
        self.__EditForm = None
        self.__EditForm = frm
        self.afterCreateEditForm.emit(JPEditFormDataMode.New)
        frm.exec_()

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return
        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=self.SQL_EditForm_Sub,
                               edit_mode=JPEditFormDataMode.Edit,
                               PKValue=cu_id)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshListForm)
        self.__EditForm = None
        self.__EditForm = frm
        self.afterCreateEditForm.emit(JPEditFormDataMode.Edit)
        frm.exec_()

    @pyqtSlot()
    def on_CmdBrowse_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return
        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=self.SQL_EditForm_Sub,
                               edit_mode=JPEditFormDataMode.ReadOnly,
                               PKValue=cu_id)
        frm.setListForm(self)
        self.__EditForm = None
        self.__EditForm = frm
        self.afterCreateEditForm.emit(JPEditFormDataMode.ReadOnly)
        frm.exec_()

    @pyqtSlot()
    def on_CmdRefresh_clicked(self):
        self.refreshListForm()

    @pyqtSlot()
    def on_CmdDelete_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return
        if self.beforeDeleteRow(cu_id):
            msg = "确认要删除记录【{}】吗？".format(cu_id)
            if QMessageBox.question(self, '确认', msg, QMessageBox.Yes,
                                    QMessageBox.Yes) == QMessageBox.Yes:
                db = JPDb()
                info = self.model.TabelFieldInfo
                sql = "delete from {tn} where {pk_n}='{pk_v}'"
                sql = sql.format(tn=self.EditFormMainTableName,
                                 pk_n=self.EditFormPrimarykeyFieldName,
                                 pk_v=cu_id)
                if db.executeTransaction(sql):
                    del_i = (
                        self.tableView.selectionModel().currentIndex().row())
                    info.deleteRow(del_i)
