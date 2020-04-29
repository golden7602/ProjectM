from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import (QMetaObject, Qt, pyqtSlot, QThread, QModelIndex)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QTreeWidgetItem,
                             QTreeWidgetItemIterator, QWidget)

from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Query import JPTabelFieldInfo
from lib.JPFunction import JPDateConver, md5_passwd
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from Ui.Ui_FormUser import Ui_Form as Ui_Form_List
from Ui.Ui_FormUserEdit import Ui_Form as Ui_Form_Edit
from PyQt5.QtGui import QColor
from lib.JPPublc import JPUser, JPPub


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, tableView, tabelFieldInfo):
        super().__init__(tableView, tabelFieldInfo)

    def data(self, Index, role=Qt.DisplayRole):
        r = Index.row()
        if (role == Qt.TextColorRole
                and self.TabelFieldInfo.DataRows[r].Datas[5] == "Non"):
            return QColor(Qt.red)

        return super().data(Index, role)


class Form_User(QWidget):
    def __init__(self, mainform):
        super().__init__(mainform)
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MianForm = mainform
        mainform.addForm(self)
        tr = self.ui.treeWidget
        tr.setColumnCount(2)
        tr.setHeaderLabels(["权限分配 Permission Assignment", "Right"])
        tr.setColumnWidth(0, 300)
        tr.setColumnWidth(1, 100)
        tr.itemChanged.connect(self.onItemChanged)
        self.refreshTable()
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

    def UserSaveData(self, tbName):
        if tbName == 'sysusers':
            self.refreshTable()

    def refreshTable(self):
        self.SQL = """
            select
                fUserID as `编号 ID`,
                fUsername as `用户名Name`,
                fNickname as `昵称Nickname`,
                fDepartment as `部门Department`,
                fNotes as `备注Note `,
                case fEnabled when 1 then '' else 'Non' end as 可用Enabled
                from  sysusers
            where  fUserID > 1
        """

        tb = self.ui.tableView
        self.dataInfo = JPTabelFieldInfo(self.SQL)
        self.mod = myJPTableViewModelReadOnly(tb, self.dataInfo)
        tb.setModel(self.mod)
        tb.resizeColumnsToContents()

        self.SQL_EditForm_Main = """
                select fUserID as `编号 ID`,
                fUsername as `用户名Name` ,
                fNickname as `昵称Nickname`,
                fDepartment as `部门Department`,
                fPassword as 密码Password,
                fNotes as `备注Note` , fEnabled
                from sysusers  WHERE fUserID = '{}'"""

        tb.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(
            self.on_tableView_currentChanged)

    def checkDirty(self):
        try:
            return self.ui.treeWidget.dirty
        except AttributeError:
            return False

    def onItemChanged(self, item):
        item.dirty = True
        self.ui.treeWidget.dirty = True

        self.ui.treeWidget.itemChanged.disconnect(self.onItemChanged)
        if item.checkState(1) == Qt.Checked:
            self.__ChangeParentCheckStateToChecked(item)
        if item.checkState(1) == Qt.Unchecked:
            self.__ChangeChildrenCheckStateToUnchecked(item)
        self.ui.treeWidget.itemChanged.connect(self.onItemChanged)

    def __ChangeChildrenCheckStateToUnchecked(self, item):
        """递归修改下级为未选中"""
        for i in range(item.childCount()):
            item_i = item.child(i)
            item_i.setCheckState(1, Qt.Unchecked)
            self.__ChangeChildrenCheckStateToUnchecked(item_i)

    def __ChangeParentCheckStateToChecked(self, item):
        """递归修改上级为选中"""
        if item.parent() is self.ui.treeWidget._rootItem:
            return
        else:
            item.parent().setCheckState(1, Qt.Checked)
            self.__ChangeParentCheckStateToChecked(item.parent())

    def on_tableView_currentChanged(self, index1, index2):
        if index2.row() != -1:
            if self.checkDirty():
                self.saveRight(index2)
        uid = self.dataInfo.DataRows[index1.row()].Data(0)
        ins_sql = """
            INSERT INTO sysuserright (fUserID, fRightID, fHasRight)
            SELECT {uid}, fNMID, fDefault
            FROM sysnavigationmenus
            WHERE fEnabled = 1
                AND NOT fNMID IN (
                    SELECT fRightID
                    FROM sysuserright
                    WHERE fUserID = {uid})"""
        sql = """
            SELECT u.fUsername, m.*, ord(ur.fHasRight) AS fHasRight
            FROM sysnavigationmenus m
                LEFT JOIN sysuserright ur ON m.fNMID = ur.fRightID
                LEFT JOIN sysusers u ON ur.fUserID = u.fUserID
            WHERE ur.fUserID = {}
                AND ord(m.fEnabled) = 1
            ORDER BY fDispIndex
        """
        db = JPDb()
        db.executeTransaction(ins_sql.format(uid=uid))
        items = db.getDict(sql.format(uid))
        self.ui.treeWidget.itemChanged.disconnect(self.onItemChanged)
        loadTreeview(self.ui.treeWidget, items)
        self.ui.treeWidget.itemChanged.connect(self.onItemChanged)

    def getCurrentUID(self, index=None):
        tr = self.ui.tableView
        r = index if index else tr.currentIndex()
        if r == -1:
            return
        index1 = self.mod.createIndex(r.row(), 0)
        return self.mod.data(index1, Qt.EditRole)

    def saveRight(self, index2):
        uid = self.getCurrentUID(index2)
        tr = self.ui.treeWidget
        index = self.mod.createIndex(index2.row(), 0)
        uid = self.mod.data(index, Qt.EditRole)
        cursor = QTreeWidgetItemIterator(tr)
        sql = """UPDATE sysuserright set fHasRight={}
                where fUserID={} and fRightID={}"""
        lst = []
        while cursor.value():
            item = cursor.value()
            if item.dirty:
                st = 1 if item.checkState(1) == Qt.Checked else 0
                lst.append(sql.format(st, uid, item.jpData['fNMID']))
            cursor = cursor.__iadd__(1)
        if lst:
            if QMessageBox.question(self, '提示', "用户权限被修改，是否保存？",
                                    (QMessageBox.Yes | QMessageBox.No),
                                    QMessageBox.Yes) == QMessageBox.Yes:
                return JPDb().executeTransaction(lst)
            else:
                return True
        else:
            return True

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        return EditForm_User(sql_main=sql_main,
                             edit_mode=edit_mode,
                             PKValue=PKValue)

    def getCurrentSelectPKValue(self):
        index = self.ui.tableView.selectionModel().currentIndex()
        if index.isValid():
            return self.mod.TabelFieldInfo.getOnlyData([index.row(), 0])

    @pyqtSlot()
    def on_CmdNew_clicked(self):
        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.New,
                               PKValue=None)
        frm.ui.fEnabled.refreshValueNotRaiseEvent(2)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshTable)
        self.__EditForm = frm
        frm.exec_()

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        errt = '编辑用户信息时，必须修改用户密码。\n'
        errt = errt + 'When editing user information, '
        errt = errt + 'user passwords must be changed'
        QMessageBox.information(None, '提示', errt)
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
    def on_CmdDelete_clicked(self):
        uid = self.getCurrentUID()
        if uid is None:
            return
        sql = "update sysusers set fEnabled=0 where fUserID={}"
        if QMessageBox.question(self, '提示', "确认要删除此用户？",
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            JPDb().executeTransaction(sql.format(uid))
            JPPub().broadcastMessage(tablename="sysusers",action='delete',PK=uid)
            self.mod.removeRow(
                self.ui.tableView.selectionModel().currentIndex().row())


def loadTreeview(treeWidget, items, hasCommandButton=False):
    class MyThreadReadTree(QThread):
        """加载功能树的线程类"""
        def __init__(self, treeWidget, items):
            super().__init__()
            treeWidget.clear()
            title1 = "权限分配 Permission Assignment【{}】"
            tree_title = [title1.format(items[0]['fUsername']), "Right"]
            treeWidget.setHeaderLabels(tree_title)
            treeWidget.dirty = False
            root = QTreeWidgetItem(treeWidget)
            root.setText(0, "Function")
            root.FullPath = "Function"
            root.key = 1
            root.dirty = False
            treeWidget._rootItem = root
            self.root = root
            self.items = items
            self.icopath = JPPub().MainForm.icoPath

        def addItems(self, parent, items):
            for r in items:
                item = QTreeWidgetItem(parent)
                item.setText(0, r["fMenuText"])
                if r["fIcon"]:
                    item.setIcon(0, QIcon(self.icopath.format(r["fIcon"])))
                st = (Qt.Checked if r['fHasRight'] == 1 else Qt.Unchecked)
                if not r["fDefault"]:
                    item.setCheckState(1, st)
                item.jpData = r
                item.dirty = False
                item.FullPath = (parent.FullPath + '\\' + r["fMenuText"])
                self.addItems(
                    item,
                    [l for l in self.items if l["fParentId"] == r["fNMID"]])
                item.setExpanded(1)

        def run(self):  # 线程执行函数
            self.addItems(self.root,
                          [l for l in self.items if l["fParentId"] == 1])
            self.root.setExpanded(True)

        def getRoot(self):
            return

    _readTree = MyThreadReadTree(treeWidget, items)
    _readTree.run()


class EditForm_User(JPFormModelMain):
    def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)

        MF = JPPub().MainForm
        MF.addLogoToLabel(self.ui.label_logo)
        MF.addOneButtonIcon(self.ui.butSave, 'save.png')
        MF.addOneButtonIcon(self.ui.butCancel, 'cancel.png')
        self.readData()
        self.ui.fUserID.setEnabled(False)
        self.ui.fPassword.setEnabled(True)
        self.ui.fPassword.refreshValueNotRaiseEvent("1234", True)
        self.ui.fPassword.passWordConver = md5_passwd

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

    def onAfterSaveData(self, data):
        # 重新加载一次用户数据
        JPUser().INIT()
        act = 'new' if self.isNewMode else 'edit'
        JPPub().broadcastMessage(tablename="sysusers",
                                 PK=data,
                                 action=act)
        super().onAfterSaveData(data)
