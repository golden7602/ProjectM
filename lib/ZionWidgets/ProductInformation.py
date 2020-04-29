import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())

from PyQt5.QtCore import Qt, QDate, QModelIndex, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import (QLineEdit, QWidget, QFileDialog, QMessageBox,
                             QPushButton, QItemDelegate)

from lib.JPPublc import JPDb, JPPub
from Ui.Ui_FormProductList import Ui_Form as UiFormProductList
from lib.JPDatabase.Query import JPTabelFieldInfo, JPQueryFieldInfo
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPFunction import JPDateConver
from lib.JPFunction import GetFileMd5
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from Ui.Ui_FormProcuctEdit import Ui_Form as Ui_Form_Edit
from lib.JPForms.JPSearch import Form_Search
from lib.ZionWidgets.ViewPic import Form_ViewPic
from lib.ZionReport.ProductListReport import (FormReport_ProductInfo,
                                              FormReport_ProductInfo_Detail,
                                              FormReport_ProductInfo_low)


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
        try:
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
        except Exception as identifier:
            pass

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


class Form_ProductList(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = UiFormProductList()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        self.list_sql = """
            select 
            fID as `序号NO.`, 
            fProductName as `产品名称Descrição do produto`, 
            fCurrentQuantity as 当前库存Quantidade ,
            fMinimumStock as 最低库存MinimumStock,
            fSpesc as  `规格Especificação`, 
            fWidth as 宽Largura, 
            fLength as 长Longo, 
            fUint 单位Unidade, 
            fNote as 备注Observações,
            fProductPic as Pic
            from t_product_information 
            where fCancel=0 and fProductName like '%{key}%' 
            order by  fID
            """
        medit_sql = """
            select fID,fProductName as 产品名称ProductName,
            fSpesc,fWidth,fLength,fUint,fNote,
            fMinimumStock,fProductPic from t_product_information where fID={}"""

        self.dataInfo_low = None
        self.dataInfo_detail = None
        self.sql_detail = None

        icon = QIcon(JPPub().MainForm.icoPath.format("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        action.triggered.connect(self.actionClick)

        self.SQL_EditForm_Main = medit_sql
        self.actionClick()
        self.dispAlertStock()
        self.pub = JPPub()

        self.ui.dateBegin.setDate(QDate(QDate.currentDate().year(), 1, 1))
        self.ui.dateEditEnd.setDate(QDate().currentDate())

        self.ui.dateBegin.dateChanged.connect(self.dispDetail)
        self.ui.dateEditEnd.dateChanged.connect(self.dispDetail)
        #self.pub.UserSaveData.connect(self.UserSaveData)

        mainform.addOneButtonIcon(self.ui.CmdPrint_Low, 'print.png')
        mainform.addOneButtonIcon(self.ui.CmdExportToExcel_Low,
                                  'exportToexcel.png')
        mainform.addOneButtonIcon(self.ui.CmdPrint_Detail, 'print.png')
        mainform.addOneButtonIcon(self.ui.CmdExportToExcel_Detail,
                                  'exportToexcel.png')

        de = MyButtonDelegate(self.ui.tableView, self.dataInfo)
        self.ui.tableView.setItemDelegateForColumn(9, de)

    def cellButtonClicked(self):
        r = self.ui.tableView.currentIndex()
        fn = self.dataInfo.DataRows[r.row()].Datas[9]
        Form_ViewPic(self, fn)

    def actionClick(self):
        txt = self.ui.lineEdit.text()
        txt = txt if txt else ''
        sql = self.list_sql.format(key=txt)
        tv = self.ui.tableView
        self.dataInfo = JPTabelFieldInfo(sql)
        self.mod = myJPTableViewModelReadOnly(tv, self.dataInfo)
        tv.setModel(self.mod)
        # de = MyButtonDelegate(tv, self.dataInfo)
        # tv.setItemDelegateForColumn(9, de)
        tv.resizeColumnsToContents()
        self.ui.tableView.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(self.dispDetail)
        self.dispDetail()

    def dispAlertStock(self):
        self.sql_low = """select              
            fID as `序号NO.`, 
            fProductName as `产品名称Descrição do produto`, 
            fCurrentQuantity as 当前库存Quantidade ,
            fMinimumStock as 最低库存MinimumStock
            from t_product_information 
            where fCancel=0 and fCurrentQuantity<fMinimumStock
            order by  fID
            """
        tv = self.ui.tableView_low
        self.dataInfo_low = JPTabelFieldInfo(self.sql_low)
        self.mod_low = myJPTableViewModelReadOnly(tv, self.dataInfo_low)
        tv.setModel(self.mod_low)
        tv.resizeColumnsToContents()
        bz = (len(self.dataInfo_low) > 0)
        self.ui.CmdExportToExcel_Low.setEnabled(bz)
        self.ui.CmdPrint_Low.setEnabled(bz)

    def dispDetail(self):
        pid = -1
        tv = self.ui.tableView
        index = tv.selectionModel().currentIndex()
        if index.isValid():
            pid = self.dataInfo.getOnlyData([index.row(), 0])
        d1 = JPDateConver(self.ui.dateBegin.date(), str)
        d2 = JPDateConver(self.ui.dateEditEnd.date(), str)
        self.sql_detail = f"""
            SELECT q.fOrderDate AS 日期OrderDate,
                    q.fOrderID AS 单据号码OrderID,
                    ksmc AS 客商Merchants,
                    rk AS 入库In ,
                    ck AS 出库Out
            FROM 
                (SELECT o.fOrderDate,
                    o.fOrderID,
                    s.fSupplierName AS ksmc,
                    d.fQuant AS rk,
                    null AS ck,
                    d.TS
                FROM t_product_warehousereceipt_order_detail AS d
                LEFT JOIN t_product_warehousereceipt_order AS o
                    ON d.fOrderID=o.fOrderID
                LEFT JOIN t_supplier AS s
                    ON o.fSupplierID=s.fSupplierID
                WHERE o.fOrderDate
                    BETWEEN '{d1}'
                        AND '{d2}'
                        AND fProductID={pid}
                        AND o.fSubmited=1
                UNION all
                SELECT o.fOrderDate,
                    o.fOrderID,
                    s.fCustomerName AS ksmc,
                    NULL AS rk,
                    d.fQuant AS ck,
                    d.TS
                FROM t_product_outbound_order_detail AS d
                LEFT JOIN t_product_outbound_order AS o
                    ON d.fOrderID=o.fOrderID
                LEFT JOIN t_customer AS s
                    ON o.fCustomerID=s.fCustomerID
                WHERE o.fOrderDate
                    BETWEEN '{d1}'
                        AND '{d2}' 
                        AND fProductID={pid}
                        AND o.fSubmited=1
                ) AS q
            ORDER BY  q.Ts DESC 
        """
        self.dataInfo_detail = JPQueryFieldInfo(self.sql_detail)
        self.mod3 = JPTableViewModelReadOnly(self.ui.tableView_rec,
                                             self.dataInfo_detail)
        self.ui.tableView_rec.setModel(self.mod3)
        self.ui.tableView_rec.resizeColumnsToContents()
        bz = (len(self.dataInfo_detail) > 0)
        self.ui.CmdExportToExcel_Detail.setEnabled(bz)
        self.ui.CmdPrint_Detail.setEnabled(bz)

    def getCurrentSelectPKValue(self):
        index = self.ui.tableView.selectionModel().currentIndex()
        if index.isValid():
            return self.mod.TabelFieldInfo.getOnlyData([index.row(), 0])

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
        frm = EditForm_Product(sql_main=sql_main,
                               edit_mode=edit_mode,
                               PKValue=PKValue)
        frm.afterSaveData.connect(self.refreshTable)
        frm.setListForm(self)
        return frm

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.mod.TabelFieldInfo,
                                           self.MainForm)
        exp.run()

    @pyqtSlot()
    def on_CmdExportToExcel_Low_clicked(self):
        if self.dataInfo_low:
            exp = JPExpExcelFromTabelFieldInfo(self.dataInfo_low,
                                               self.MainForm)
            exp.run()

    @pyqtSlot()
    def on_CmdExportToExcel_Detail_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.dataInfo_detail, self.MainForm)
        exp.run()

    @pyqtSlot()
    def on_CmdSearch_clicked(self):
        frm = Form_Search(self.dataInfo, self.list_sql.format(wherestring=''))
        frm.whereStringCreated.connect(self.actionClick)
        frm.exec_()

    @pyqtSlot()
    def on_CmdPrint_clicked(self):
        rpt = FormReport_ProductInfo()
        rpt.initItem()
        rpt.BeginPrint()

    @pyqtSlot()
    def on_CmdPrint_Low_clicked(self):
        rpt = FormReport_ProductInfo_low()
        rpt.initItem()
        rpt.BeginPrint()

    @pyqtSlot()
    def on_CmdPrint_Detail_clicked(self):
        if self.sql_detail:
            rpt = FormReport_ProductInfo_Detail()
            rpt.sql = self.sql_detail
            rpt.beginDate = self.ui.dateBegin.date()
            rpt.endDate = self.ui.dateEditEnd.date()
            rpt.initItem()
            rpt.BeginPrint()

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
        pid = self.getCurrentSelectPKValue()
        if pid is None:
            return
        sql0 = f"""
            select fProductID from 
            t_product_outbound_order_detail 
            where fProductID={pid} Limit 1 
            union all 
            select fProductID 
            from t_product_warehousereceipt_order_detail 
            where fProductID={pid} Limit 1 """
        tab = JPQueryFieldInfo(sql0)
        if len(tab):
            txt = '该产品已经存在订单，无法删除!\n'
            txt = txt + "The product already has an order and can not delete it!"
            QMessageBox.warning(self, '提示', txt, QMessageBox.Cancel,
                                QMessageBox.Cancel)
            return
        del_txt = '确认要删除此产品？\n'
        del_txt = del_txt + 'Are you sure you want to delete this product?'
        sql = f"DELETE FROM t_product_information WHERE fID = {pid}"
        if QMessageBox.question(self, '提示', del_txt,
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            JPDb().executeTransaction(sql)
            self.refreshTable()


class EditForm_Product(JPFormModelMain):
    def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)
        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        JPPub().MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
        JPPub().MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')

        self.ui.fProductPic.hide()

        self.readData()
        pic = self.ui.label_Tax_Registration
        self.ui.fID.setEnabled(False)
        self.ui.fProductName.setFocus()
        pic.to_FullPath = None
        pic.NewFileName = None
        pic.setScaledContents(False)
        pic.setWordWrap(True)
        self.dispPixmap = None
        fn_m = self.mainTableFieldsInfo.DataRows[0].Datas[8]
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
        self.ui.fProductPic.refreshValueNotRaiseEvent(saveName, True)
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
                #JPPub().INITProduct()
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
        JPPub().broadcastMessage(tablename="t_Product", action=act, PK=data)
        super().onAfterSaveData(data)
