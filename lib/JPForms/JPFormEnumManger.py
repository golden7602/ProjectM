import datetime
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QWidget, QAbstractItemView, QMenu, QAction,
                             QMessageBox)
from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot
from Ui.Ui_FormEnum import Ui_Form as Ui_Form_list
from Ui.Ui_FormEnumEdit import Ui_Form as Ui_Form_Edit
from lib.JPDatabase.Query import JPQueryFieldInfo, JPTabelFieldInfo
from lib.JPMvc.JPModel import (JPTableViewModelReadOnly)
from lib.JPMvc.JPEditFormModel import JPFormModelMain, JPEditFormDataMode
from lib.JPPublc import JPDb, JPPub


class _myReadOnlyMod(JPTableViewModelReadOnly):
    def __init__(self, tableView, tabelFieldInfo):
        super().__init__(tableView, tabelFieldInfo)

    def data(self, Index, role):
        if role == Qt.TextAlignmentRole and Index.column() == 0:
            return Qt.AlignCenter
        else:
            return super().data(Index, role)


class Form_EnumManger(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.CurrentTypeID = None
        ui = Ui_Form_list()
        ui.setupUi(self)
        sql1 = """SELECT fTypeID AS 'TypeID 类别ID',
                    fTypeName AS 'TypeName 名称',
                    fNote AS 'Note 说明'
                FROM t_enumeration_type
                ORDER BY fTypeID
        """
        self.ui = ui
        mainform.addOneButtonIcon(ui.butNew, "new.png")
        self.tab1 = ui.tabelViewType
        self.tab2 = ui.tabelViewEnum
        self.mainform = mainform
        self.tab1.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tab2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tab1.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabinfo1 = JPQueryFieldInfo(sql1)
        self.mod1 = _myReadOnlyMod(self.tab1, self.tabinfo1)
        self.tab1.setModel(self.mod1)
        self.tab1.resizeColumnsToContents()
        mainform.addForm(self)
        self.tab1.selectionModel().currentRowChanged.connect(
            self.type_selected)

        self.setTab2Column()
        self.refreshTabEnum()
        self.ui.butNew.clicked.connect(self.but_New)

    def type_selected(self, index1, index2):
        self.CurrentTypeID = self.tabinfo1.getOnlyData([index1.row(), 0])
        self.refreshTabEnum(self.CurrentTypeID)

    def refreshTabEnum(self, type_id: int = -1):
        sql2 = """
        SELECT fItemID, fTypeID,
            fTitle AS 'text条目文本',
            fSpare1 AS 'Value1值1',
            fSpare2 AS 'Value2值2',
            fNote AS 'Note说明'
        FROM t_enumeration
        WHERE fTypeID = {}
        """.format(type_id)
        self.tabinfo2 = JPTabelFieldInfo(sql2)
        self.mod2 = JPTableViewModelReadOnly(self.tab2, self.tabinfo2)
        self.tab2.setModel(self.mod2)
        self.setTab2Column()

    def but_New(self):
        tid = self.CurrentTypeID
        if tid is None:
            return
        sql = """select fItemID,fTypeID,
                fTitle AS 'text条目文本',
                fSpare1 AS 'Value1值1',
                fSpare2 AS 'Value2值2',
                fNote AS 'Note说明'
                from t_enumeration where fItemID='{}'"""
        frm = EditForm_Enum(sql, None, JPEditFormDataMode.New, tid)
        frm.afterSaveData.connect(self.refreshsub)
        frm.exec_()

    def refreshsub(self, ID):
        self.refreshTabEnum(self.CurrentTypeID)
        self._locationRow(ID)

    def setTab2Column(self):
        self.tab2.setColumnHidden(0, True)
        self.tab2.setColumnHidden(1, True)
        self.tab2.setColumnWidth(2, 300)
        self.tab2.setColumnWidth(3, 100)
        self.tab2.setColumnWidth(4, 100)
        self.tab2.setColumnWidth(5, 300)

    def _locationRow(self, id):
        tab = self.tabinfo2
        c = tab.PrimarykeyFieldIndex
        id = int(id)
        target = [
            i for i, r in enumerate(tab.DataRows)
            if tab.getOnlyData([i, c]) == id
        ]
        if target:
            index = self.mod2.createIndex(target[0], c)
            self.ui.tabelViewEnum.setCurrentIndex(index)
            return


class EditForm_Enum(JPFormModelMain):
    def __init__(self,
                 sql_main,
                 PKValue,
                 edit_mode,
                 TypeID,
                 flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)
        pix = QPixmap(getcwd() + "\\res\\tmLogo100.png")
        self.ui.label_logo.setPixmap(pix)
        self.readData()
        self.ui.fTypeID.refreshValueNotRaiseEvent(TypeID)
        self.ui.butPrint.hide()
        self.ui.butPDF.hide()
        self.ui.fItemID.hide()
        self.ui.fTypeID.setEnabled(False)

    def onGetFieldsRowSources(self):
        db = JPDb()
        lst = db.getDataList(
            "select fTypeName,fTypeID from t_enumeration_type")
        return [('fTypeID', lst, 1)]

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

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
                JPPub().INITEnum()
        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()
