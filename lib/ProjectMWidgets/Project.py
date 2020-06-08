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
from Ui.Ui_FormProjectInfoEdit import Ui_Form as Ui_Form_Edit
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPForms.JPFormSearch import Form_Search
from threading import Thread
from lib.JPForms.JPFormViewPic import Form_ViewPic
from lib.JPFunction import GetFileMd5
import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())

# class MyCopyFileError(Exception):
#     def __init__(self, from_path, to_path, old_msg, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         errstr = "保存文件过程中出现错误,但数据已经成功保存！"
#         errstr = errstr + 'An error occurred while saving the file\n'
#         errstr = errstr + f'From:{from_path}\n'
#         errstr = errstr + f'To:{to_path}\n'
#         errstr = errstr + old_msg
#         self.errstr = errstr

#     def __str__(self):
#         return self.errstr


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        if c == 9 and role == Qt.DisplayRole:
            return ''
        else:
            return super().data(index, role)

class Form_Project(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        self.list_sql = """
            SELECT p.project_pk               AS 项目编号,
                o.org_simple_name          AS 实施单位,
                p.project_simple_name      AS 项目简称,
                e_category.fTitle          AS 类别,
                e_state.fTitle             AS 状态,
                p.required_completion_date AS 要求完成日期,
                e_key_project_level.fTitle AS 重点项目级别,
                e_construction_mode.fTitle AS 建设模式,
                p.investor                 AS 投资方,
                p.location                 AS 位置,
                p.approval_date            AS 立项日期,
                p.commencement             AS 开工日期
            FROM   (((((t_project_base_info p
                        LEFT JOIN t_org_info o
                            ON(( p.org_pk = o.org_pk )))
                    LEFT JOIN t_enumeration e_state
                            ON(( p.state = e_state.fItemID )))
                    LEFT JOIN t_enumeration e_category
                            ON(( p.category = e_category.fItemID )))
                    LEFT JOIN t_enumeration e_key_project_level
                            ON(( p.key_project_level = e_key_project_level.fItemID )))
                    LEFT JOIN t_enumeration e_construction_mode
                        ON(( p.construction_mode = e_construction_mode.fItemID )))
                    {wherestring}
                        """
        medit_sql = """
                select 
                project_pk, 
                project_name, 
                investor, 
                org_pk, 
                project_simple_name, 
                construction_mode, 
                location, 
                content, 
                floorage, 
                estimated_total_investment, 
                key_project_level, 
                category, 
                state, 
                approval_date, 
                commencement, 
                required_completion_date, 
                completion_date, 
                land_certificate, 
                call_for_bids, 
                builders_license,
                required_commencement 
                from  t_project_base_info 
                where 
                project_pk = '{}'"""

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
        if tbName == 't_project_base_info':
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
            org_simple_name like '%{key}%' or
            project_simple_name like '%{key}%' or
            key_project_level like '%{key}%' or
            investor like '%{key}%' or
            construction_mode like '%{key}%' or
            category like '%{key}%'
        )"""
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
        frm = EditForm_Project(sql_main=sql_main,
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
        sql = """select a.archives_pk from t_archives as a 
                right join t_archives_project as p 
                on a.archives_pk=p.archives_pk  
                where p.project_pk={}"""
        lst = JPDb().getDataList(sql.format(uid))
        if lst:
            lst1=[]
            for i in lst:
                for y in i:
                    lst1.append(str(y))
            s = ",".join(lst1)
            errStr = '以下档案关联本项目，无法删除\n'+ s
            msgBox = QMessageBox(QMessageBox.Critical, u'错误', errStr)
            msgBox.exec_()
            return
        del_txt = '确认要删除此项目？\n'
        del_txt = del_txt + 'Are you sure you want to delete this Project?'
        sql = "DELETE FROM t_project_base_info WHERE project_pk = {}"
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


class EditForm_Project(JPFormModelMain):
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
        self.ui.project_pk.setEnabled(False)

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

    def onGetFieldsRowSources(self):
        pub = JPPub()
        sql = """select CONCAT(rpad(org_simple_name,7,'  '),'->',org_name), org_pk
                    from t_org_info 
                    order by CONVERT(org_simple_name USING gbk)"""
        lstOrg = JPDb().getDataList(sql)
        return [
            ('state', pub.getEnumList(1), 1),
            ('category', pub.getEnumList(2), 1),
            ('key_project_level', pub.getEnumList(3), 1),
            ('construction_mode', pub.getEnumList(4), 1),
            ('org_pk', lstOrg, 1)
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
        JPPub().broadcastMessage(tablename="t_project_base_info",
                                 action=act,
                                 PK=data)
        super().onAfterSaveData(data)
