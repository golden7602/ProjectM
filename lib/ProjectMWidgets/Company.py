from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from PyQt5.QtCore import QDate, QMetaObject, pyqtSlot, Qt, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog, QItemDelegate)
from lib.JPDatabase.Query import JPTabelFieldInfo
from lib.JPFunction import JPDateConver
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPublc import JPDb, JPPub
from Ui.Ui_FormProjectList import Ui_Form as Ui_Form_List
from Ui.Ui_FormCompanyEdit import Ui_Form as Ui_Form_Edit
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPForms.JPFormSearch import Form_Search
from threading import Thread
from lib.JPForms.JPFormViewPic import Form_ViewPic
from lib.JPFunction import GetFileMd5
import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        if c == 9 and role == Qt.DisplayRole:
            return ''
        else:
            return super().data(index, role)


class Form_Company(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        self.list_sql = """
            select 
            o.org_pk as 公司编号, 
            o.org_name as 公司名称, 
            o.org_simple_name as 简称, 
            o1.org_name as 上级公司, 
            o.statistician as 统计员 ,
            if(o.deleted=1,'删除','') as 删除
            from 
            t_org_info as o
            left join t_org_info as o1 on o.org_parent=o1.org_pk
                    {wherestring}
                        """
        medit_sql = """
            select 
            org_pk, 
            org_name , 
            org_simple_name, 
            org_parent , 
            statistician  
            from 
                t_org_info 
            where org_pk = '{}'"""

        icon = QIcon(JPPub().getIcoPath("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        #self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        action.triggered.connect(self.actionClick)

        self.SQL_EditForm_Main = medit_sql
        self.actionClick()
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

    def UserSaveData(self, tbName):
        if tbName == 't_org_info':
            self.actionClick()

    def __getUID(self):
        r = self.ui.tableView.currentIndex()
        if r:
            return self.dataInfo.DataRows[r.row()].Datas[0]
        else:
            return -1

    def cellButtonClicked(self):
        r = self.ui.tableView.currentIndex()
        fn = self.dataInfo.DataRows[r.row()].Datas[9]
        Form_ViewPic(self, fn)

    def actionClick(self, where_sql=None):
        wherestring = """where (
            o.org_name like '%{key}%' or
            o.org_parent like '%{key}%' or
            o.org_simple_name like '%{key}%' or
            o.statistician like '%{key}%'
        ) """
        txt = self.ui.lineEdit.text()
        txt = txt if txt else ''
        wherestring = wherestring.format(key=txt)
        sql = where_sql if where_sql else self.list_sql.format(
            wherestring=wherestring)

        tv = self.ui.tableView
        self.dataInfo = JPTabelFieldInfo(sql)
        self.mod = myJPTableViewModelReadOnly(tv, self.dataInfo)
        tv.setModel(self.mod)
        #de = MyButtonDelegate(tv, self.dataInfo)
        #tv.setItemDelegateForColumn(9, de)
        tv.resizeColumnsToContents()

    def _locationRow(self, id):
        tab = self.dataInfo
        c = tab.PrimarykeyFieldIndex
        id = int(id)
        target = [
            i for i, r in enumerate(tab.DataRows)
            if tab.getOnlyData([i, c]) == id
        ]
        if target:
            index = self.mod.createIndex(target[0], c)
            self.ui.tableView.setCurrentIndex(index)
            return

    def refreshTable(self, ID=None):
        self.ui.lineEdit.setText(None)
        self.actionClick()
        if ID:
            self._locationRow(ID)

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        frm = EditForm_Company(sql_main=sql_main,
                               edit_mode=edit_mode,
                               PKValue=PKValue)
        frm.afterSaveData.connect(self.refreshTable)
        frm.setListForm(self)
        return frm

    def getCurrentSelectPKValue(self):
        index = self.ui.tableView.selectionModel().currentIndex()
        if index.isValid():
            return self.mod.TabelFieldInfo.getOnlyData([index.row(), 0])

    @pyqtSlot()
    def on_CmdSearch_clicked(self):
        frm = Form_Search(self.dataInfo, self.list_sql.format(wherestring=''))
        frm.whereStringCreated.connect(self.actionClick)
        frm.exec_()

    @pyqtSlot()
    def on_CmdRefresh_clicked(self):
        self.actionClick()

    @pyqtSlot()
    def on_CmdNew_clicked(self):

        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.New,
                               PKValue=None)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshTable)
        self.__EditForm = frm
        frm.exec_()

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return

        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.Edit,
                               PKValue=cu_id)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshTable)
        self.__EditForm = frm
        frm.exec_()

    @pyqtSlot()
    def on_CmdBrowse_clicked(self):
        self.setCursor(Qt.WaitCursor)
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return

        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.ReadOnly,
                               PKValue=cu_id)
        frm.setListForm(self)
        self.__EditForm = frm
        frm.exec_()
        self.setCursor(Qt.ArrowCursor)

    @pyqtSlot()
    def on_CmdDelete_clicked(self):
        uid = self.getCurrentSelectPKValue()
        if uid is None:
            return
        del_txt = '确认要删除此公司？\n'
        del_txt = del_txt + 'Are you sure you want to delete this company?'
        sql = "update t_org_info set deleted=1 where org_pk='{}'"
        if QMessageBox.question(self, '提示', del_txt,
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            JPDb().executeTransaction(sql.format(uid))
            self.refreshTable()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.mod.TabelFieldInfo,
                                           self.MainForm)
        exp.run()


class EditForm_Company(JPFormModelMain):
    def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)
        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        JPPub().MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
        JPPub().MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')
        self.readData()
        self.ui.org_pk.setEnabled(False)
        self.setPkRole(1)

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

    def onGetFieldsRowSources(self):
        sql = """select CONCAT(rpad(org_simple_name,7,'  '),'->',org_name), org_pk
                    from t_org_info 
                    order by CONVERT(org_simple_name USING gbk)"""
        lstOrg = JPDb().getDataList(sql)
        return [
            ('org_parent', lstOrg, 1)
        ]

    @pyqtSlot()
    def on_butCancel_clicked(self):
        self.close()

    @pyqtSlot()
    def on_butSave_clicked(self):
        try:
            lst0 = self.getSqls(self.PKRole)
            lst = lst0 + [JPDb().LAST_INSERT_ID_SQL()]
            isOK, result = JPDb().executeTransaction(lst)
            if isOK:
                self.ui.butSave.setEnabled(False)
                self.afterSaveData.emit(str(result))
                QMessageBox.information(self, '完成',
                                        '保存数据完成！\nSave data complete!')

        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()

    def onAfterSaveData(self, data):
        act = 'new' if self.isNewMode else 'edit'
        JPPub().broadcastMessage(tablename="t_org_info",
                                 action=act,
                                 PK=data)
        super().onAfterSaveData(data)
