import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())

from PyQt5.QtCore import QDate, QMetaObject, pyqtSlot, Qt, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog, QItemDelegate)

from lib.JPDatabase.Query import JPTabelFieldInfo
from lib.JPFunction import JPDateConver
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPublc import JPDb, JPPub
from Ui.Ui_FormSupplier import Ui_Form as Ui_Form_List
from Ui.Ui_FormSupplierEdit import Ui_Form as Ui_Form_Edit
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPForms.JPSearch import Form_Search
from threading import Thread
from lib.ZionWidgets.ViewPic import Form_ViewPic
from lib.JPFunction import GetFileMd5


class MyCopyFileError(Exception):
    def __init__(self, from_path, to_path, old_msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        errstr = "保存文件过程中出现错误,但数据已经成功保存！"
        errstr = errstr + 'An error occurred while saving the file\n'
        errstr = errstr + f'From:{from_path}\n'
        errstr = errstr + f'To:{to_path}\n'
        errstr = errstr + old_msg
        self.errstr = errstr

    def __str__(self):
        return self.errstr


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        if c == 9 and role == Qt.DisplayRole:
            return ''
        else:
            return super().data(index, role)


class MyButtonDelegate(QItemDelegate):
    def __init__(self, parent=None, dataInfo=None):
        super(MyButtonDelegate, self).__init__(parent)
        self.dataInfo = dataInfo
        self.icon = JPPub().MainForm.getIcon('rosette.ico')

    def paint(self, painter, option, index):
        curCer = self.dataInfo.DataRows[index.row()].Datas[9]
        if not self.parent().indexWidget(index) and curCer:
            widget = QPushButton(
                self.tr(''),
                self.parent(),
                clicked=self.parent().parent().cellButtonClicked)
            widget.setIcon(self.icon)
            self.parent().setIndexWidget(index, widget)
        else:
            widget = self.parent().indexWidget(index)
            if widget:
                widget.setGeometry(option.rect)

    def createEditor(self, parent, option, index):
        """有这个空函数覆盖父类的函数，才能使该列不可编辑"""
        return

    def setEditorData(self, editor, index):
        return

    def setModelData(self, editor, model, index):
        return

    def updateEditorGeometry(self, editor, StyleOptionViewItem,
                             index: QModelIndex):
        editor.setGeometry(StyleOptionViewItem.rect)


class Form_Supplier(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        self.list_sql = """
            select 
                fSupplierID as `ID`, 
                fSupplierName as `供应商名称Supplier`, 
                fNUIT as `税号NUIT`, 
                fEndereco as `地址Endereco`,
                fCity as `城市City`, 
                fContato as `联系人Contato`, 
                fCelular as `手机Celular`, 
                fEmail as `电子邮件Email`, 
                fFax as `传真Fax` ,
                fTaxRegCer as TaxCert
            from  t_supplier 
            {wherestring}
            order by fSupplierName
            """
        medit_sql = """
            select 
            fSupplierID as `ID`, 
            fSupplierName as `供应商名称Supplier`, 
            fNUIT as `税号NUIT`, 
            fEndereco,
            fCity,
            fContato,
            fCelular,
            fEmail,
            fNote,
            fFax,
            fTaxRegCer
            from  t_supplier
            where fSupplierID={} 
            order by fSupplierName"""

        icon = QIcon(JPPub().MainForm.icoPath.format("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        action.triggered.connect(self.actionClick)

        self.SQL_EditForm_Main = medit_sql
        self.actionClick()
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

    def UserSaveData(self, tbName):
        if tbName == 't_supplier':
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
            fSupplierName like '%{key}%' or
            fEndereco like '%{key}%' or
            fNUIT like '%{key}%' or
            fCity like '%{key}%' or
            fContato like '%{key}%' or
            fCelular like '%{key}%' or
            fEmail like '%{key}%' or
            fFax like '%{key}%' 
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
        de = MyButtonDelegate(tv, self.dataInfo)
        tv.setItemDelegateForColumn(9, de)
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
        frm = EditForm_Supplier(sql_main=sql_main,
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
    def on_CmdDelete_clicked(self):
        uid = self.getCurrentSelectPKValue()
        if uid is None:
            return
        sql0 = """
            SELECT fSupplierID
            FROM t_product_warehousereceipt_order
            WHERE fSupplierID = {}
            LIMIT 1"""
        tab = JPQueryFieldInfo(sql0.format(uid))
        if len(tab):
            txt = '该客户已经存在订单，无法删除!\n'
            txt = txt + "The Supplier already has an order and can not delete it!"
            QMessageBox.warning(self, '提示', txt, QMessageBox.Cancel,
                                QMessageBox.Cancel)
            return
        del_txt = '确认要删除此客户？\n'
        del_txt = del_txt + 'Are you sure you want to delete this Supplier?'
        sql = "DELETE FROM t_supplier WHERE fSupplierID = {}"
        if QMessageBox.question(self, '提示', del_txt,
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            JPDb().executeTransaction(sql.format(uid))
            self.refreshTable()


class EditForm_Supplier(JPFormModelMain):
    def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)
        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        JPPub().MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
        JPPub().MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')

        self.ui.fTaxRegCer.hide()

        self.readData()
        pic = self.ui.label_Tax_Registration
        self.ui.fSupplierID.setEnabled(False)
        self.ui.fSupplierName.setFocus()
        pic.to_FullPath = None
        pic.NewFileName = None
        pic.setScaledContents(False)
        pic.setWordWrap(True)
        self.dispPixmap = None
        fn_m = self.mainTableFieldsInfo.DataRows[0].Datas[10]
        if fn_m:
            try:
                self.dispPixmap = JPPub().MainForm.getTaxCerPixmap(fn_m)
            except FileExistsError as e:
                self.ui.label_Tax_Registration.setText('File not found!')
                # QMessageBox.warning(JPPub().MainForm, '错误', e.Msg)
        else:
            self.dispPixmap = JPPub().MainForm.getPixmap('big_certificate.png')

        if self.isReadOnlyMode:
            self.ui.btn_SelectPic.setEnabled(False)

        self.toPath = JPPub().getConfigData()['TaxRegCerPath']

    def resizeEvent(self, resizeEvent):
        if self.dispPixmap:
            size = self.ui.label_Tax_Registration.size()
            Pixmap = self.dispPixmap.scaled(size, Qt.KeepAspectRatio)
            self.ui.label_Tax_Registration.setPixmap(Pixmap)

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

    @pyqtSlot()
    def on_butCancel_clicked(self):
        self.close()

    @pyqtSlot()
    def on_btn_SelectPic_clicked(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(
            JPPub().MainForm,
            "Select a Jpeg File",
            os.getcwd(),  # 起始路径
            "Jpeg Files (*.jpg)")
        if not fileName_choose:
            return
        pic = self.ui.label_Tax_Registration
        pic.NewFileName = fileName_choose
        r_path, r_file = os.path.split(fileName_choose)
        fn_split = r_file.split(".")
        newName = GetFileMd5(fileName_choose)
        toPath = self.toPath
        fn_m = f'tax_reg_{newName}'
        fn_e = fn_split[len(fn_split) - 1]
        pic.to_FullPath = f"{toPath}\\{fn_m}.{fn_e}"
        saveName = f'{fn_m}.{fn_e}'
        self.ui.fTaxRegCer.refreshValueNotRaiseEvent(saveName, True)
        pic.setScaledContents(True)
        pic.setPixmap(QPixmap(fileName_choose))

    @pyqtSlot()
    def on_butSave_clicked(self):
        try:
            lst0 = self.getSqls(self.PKRole)
            lst = lst0 + [JPDb().LAST_INSERT_ID_SQL()]
            isOK, result = JPDb().executeTransaction(lst)
            if isOK:
                self.ui.butSave.setEnabled(False)
                self.afterSaveData.emit(str(result))
                self.__SavePic(result)
                JPPub().INITSupplier()
                QMessageBox.information(self, '完成',
                                        '保存数据完成！\nSave data complete!')

        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()

    def __SavePic(self, result):
        pic = self.ui.label_Tax_Registration
        if not (pic.to_FullPath and pic.NewFileName):
            return
        try:
            myCopy(pic.NewFileName, pic.to_FullPath)
        except Exception as e:
            raise MyCopyFileError(pic.NewFileName, pic.to_FullPath, str(e))

    def onAfterSaveData(self, data):
        act = 'new' if self.isNewMode else 'edit'
        JPPub().broadcastMessage(tablename="t_supplier",
                                 action=act,
                                 PK=data)
        super().onAfterSaveData(data)
