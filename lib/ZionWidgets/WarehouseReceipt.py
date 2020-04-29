from os import getcwd
from sys import path as jppath

jppath.append(getcwd())

from PyQt5.QtCore import QDate, QModelIndex, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QMessageBox

from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPFunction import JPRound
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMainHasSub
from lib.JPMvc.JPFuncForm import JPFunctionForm
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPrint.JPPrintReport import JPPrintSectionType
from lib.JPPublc import JPPub, JPUser
from lib.ZionReport.OrderReportMob import Order_report_Mob
from Ui.Ui_FormWarehouseReceipt import Ui_Form
from lib.ZionWidgets.ProductSelecter import ProductSelecter
from lib.ZionReport.WareHouseReceipt_Bill import WarehouseReceipt_Bill


class OutboundOrderMod(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabFont = QFont("Times", 10)
        self.tabFont.setBold(False)
        self.tabFont.setStretch(150)
        self.ok_icon = JPPub().MainForm.getIcon('yes.ico')

    def data(self, index, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        tab = self.TabelFieldInfo
        curid = tab.getOnlyData((r, 0))  # DataRows[r].Datas[0]

        submited = tab.getOnlyData((r, 2))
        if c == 2 and role == Qt.DecorationRole and submited:
            return self.ok_icon
        elif c == 2 and role == Qt.DisplayRole and submited:
            return "Submited"
        else:
            return super().data(index, role=role)


class JPFuncForm_WarehouseReceipt(JPFunctionForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        self.MainForm = MainForm
        sql_0 = """
                SELECT o.fOrderID as 入库单号OrderID,
                    fOrderDate as 日期OrderDate,
                    fSubmited as 提交,
                    fSupplierName as 供应商Supplier,
                    fWarehousingDate as 入库日期WarehousingDate,
                    fAmount as 金额SubTotal,
                    fDesconto as 折扣Desconto,
                    fTax as 税金IVA,
                    fPayable as `应付金额Valor a Pagar`,
                    o.fContato as 联系人Contato
                from t_product_warehousereceipt_order as o left join t_supplier as c on o.fSupplierID=c.fSupplierID"""
        sql_1 = sql_0 + """
                WHERE fOrderDate{date}
                AND (fSubmited={ch1} OR fSubmited={ch2})
                AND fOrderDate{date}
                ORDER BY  o.fOrderID DESC"""
        sql_2 = sql_0 + """ ORDER BY  o.fOrderID DESC"""
        self.backgroundWhenValueIsTrueFieldName = ['fSubmited']
        self.checkBox_1.setText('Submited')
        self.checkBox_2.setText('UnSubmited')
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(True)
        super().setListFormSQL(sql_1, sql_2)
        #self.tableView.setColumnHidden(13, True)
        self.fSubmited_column = 2
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

        m_sql = """
                SELECT fOrderID as 订单号码OrderID
                    , fOrderDate as 日期OrderDate
                    , fPurchaserID as 采购员Purchaser
                    , fWarehousingDate as 交货日期RequiredDeliveryDate
                    , fSupplierID  as 客户名Cliente
                    , fContato
                    , fCelular
                    , fTelefone
                    , fAmount
                    , fTax
                    , fPayable
                    , fDesconto
                    , fNote
                    , fEntryID
                FROM t_product_warehousereceipt_order
                WHERE fOrderID = '{}'
                """
        s_sql = """
                SELECT fID, fOrderID, 
                    fProductID AS '名称Descrição', fQuant AS '数量Qtd',
                    fPrice AS '单价P. Unitario', fAmount AS '金额Total'
                FROM t_product_warehousereceipt_order_detail
                WHERE fOrderID = '{}'
                """
        self.setEditFormSQL(m_sql, s_sql)

    def UserSaveData(self, tbName):
        if tbName == 't_product_warehousereceipt_order':
            self.refreshListForm()

    def onGetModelClass(self):
        return OutboundOrderMod

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):

        frm = EditForm_WarehouseReceipt(sql_main=sql_main,
                                        edit_mode=edit_mode,
                                        sql_sub=sql_sub,
                                        PKValue=PKValue)
        frm.ui.fOrderID.setEnabled(False)
        frm.ui.fCity.setEnabled(False)
        frm.ui.fNUIT.setEnabled(False)
        frm.ui.fEntryID.setEnabled(False)
        frm.ui.fEndereco.setEnabled(False)
        frm.ui.fEmail.setEnabled(False)
        return frm

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.model.TabelFieldInfo,
                                           self.MainForm)
        exp.run()

    @pyqtSlot()
    def on_CmdSubmit_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return
        db = JPDb()
        info = self.model.TabelFieldInfo
        submitted = info.getOnlyData([
            self.tableView.selectionModel().currentIndex().row(),
            self.fSubmited_column
        ])
        if submitted == 1:
            msg = '记录【{cu_id}】已经提交，不能重复提交!\nThe order [{cu_id}] '
            msg = msg + 'has been submitted, can not be repeated submission!'
            msg = msg.replace("{cu_id}", str(cu_id))
            QMessageBox.warning(self, '提示', msg, QMessageBox.Ok,
                                QMessageBox.Ok)
            return
        msg = '提交后入库单将不能修改！确定继续提交记录【{cu_id}】吗？\n'
        msg = msg + 'The order "{cu_id}" will not be modified after submission. '
        msg = msg + 'Click OK to continue submitting?'
        msg = msg.replace("{cu_id}", str(cu_id))
        reply = QMessageBox.question(self, '确认', msg,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            sql0 = f"""UPDATE t_product_warehousereceipt_order set fSubmited=1 
                where fOrderID='{cu_id}';"""
            sql1 = f"""
            UPDATE t_product_information AS p,
                (SELECT fProductID,
                    sum(fQuant) AS sum_sl
                FROM t_product_warehousereceipt_order_detail
                WHERE fOrderID='{cu_id}'
                GROUP BY  fProductID) AS q1 SET p.fCurrentQuantity=p.fCurrentQuantity+q1.sum_sl
            WHERE p.fID=q1.fProductID;
            """
            sql2 = "select '{cu_id}';"
            db.executeTransaction([sql0, sql1, sql2])
            JPPub().broadcastMessage(
                tablename="t_product_warehousereceipt_order",
                PK=cu_id,
                action='Submit')
            self.refreshListForm()

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return
        info = self.model.TabelFieldInfo
        submitted = info.getOnlyData([
            self.tableView.selectionModel().currentIndex().row(),
            self.fSubmited_column
        ])
        if submitted == 1:
            msg = '记录【{cu_id}】已经提交，不能修改!\nThe order [{cu_id}] '
            msg = msg + 'has been submitted, can not edit it!'
            msg = msg.replace("{cu_id}", str(cu_id))
            QMessageBox.warning(self, '提示', msg, QMessageBox.Ok,
                                QMessageBox.Ok)
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


class mySubMod(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def data(self, index, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        tab = self.TabelFieldInfo
        curid = tab.getOnlyData((r, 2))  # DataRows[r].Datas[0]

        if role == Qt.DisplayRole and c == 2:
            if curid:
                return self.getFullProductName(curid)
        elif role == Qt.TextAlignmentRole and c == 2:
            return (Qt.AlignLeft | Qt.AlignVCenter)

        else:
            return super().data(index, role=role)


class EditForm_WarehouseReceipt(JPFormModelMainHasSub):
    def __init__(self,
                 sql_main=None,
                 PKValue=None,
                 sql_sub=None,
                 edit_mode=JPEditFormDataMode.ReadOnly,
                 flags=Qt.WindowFlags()):
        super().__init__(Ui_Form(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         sql_sub=sql_sub,
                         edit_mode=edit_mode,
                         flags=flags)

        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        self.setPkRole(7)
        self.cacuTax = True
        self.ui.fTax.keyPressEvent = self.__onTaxKeyPress
        self.readData()
        if self.isNewMode:
            self.ObjectDict()['fEntryID'].refreshValueNotRaiseEvent(
                JPUser().currentUserID())
        else:
            self.__customerIDChanged()
        if edit_mode != JPEditFormDataMode.ReadOnly:
            self.ui.fSupplierID.setEditable(True)
        self.ui.fOrderDate.refreshValueNotRaiseEvent(QDate.currentDate())
        self.ui.fWarehousingDate.FieldInfo.NotNull = True
        self.ui.fSupplierID.setFocus()
        self.ui.tableView.keyPressEvent = self.mykeyPressEvent
        self.ui.tableView.doubleClicked.connect(self.table_change)

        self.productInfo = self.__getProductInfo()
        self.subModel.getFullProductName = self.getFullProductName
        self._setEditFormButtonsIcon(self.ui)

    def _setEditFormButtonsIcon(self, ui):
        pub = JPPub()
        fun = pub.MainForm.addOneButtonIcon
        fun(ui.butSave, "save.png")
        fun(ui.butPrint, "print.png")
        fun(ui.butPDF, "pdf.png")

    def getFullProductName(self, curid):
        if curid:
            r = self.productInfo[curid]
            r1 = [r[0]]
            for i in range(len(r)):
                if i >= 2 and r[i]:
                    r1.append(r[i])
            return " /".join(r1)

    def __getProductInfo(self):
        sql = """
        select fID,fProductName, fCurrentQuantity ,
        fSpesc,fWidth,fLength,fUint
        from t_product_information where fCancel=0
        """
        lst = JPDb().getDataList(sql)
        return {r[0]: r[1:] for r in lst}

    def onGetModelClass(self):
        return mySubMod

    def table_change(self, index1):
        def fun(p_id, product_name, fCurrentQuantity):
            tab = self.subModel.TabelFieldInfo
            tab.setData([r, 2], p_id)

        r = index1.row()
        if index1.column() == 2 and not self.isReadOnlyMode:
            frm = ProductSelecter()
            frm.ProductSeledted.connect(fun)
            frm.exec_()

    # 手动增加空行
    def mykeyPressEvent(self, KeyEvent):
        if (KeyEvent.modifiers() == Qt.AltModifier
                and KeyEvent.key() == Qt.Key_D):
            mod = self.subModel
            l = len(self.subTableFieldsInfo)
            mod.insertRows(l, 1, mod.createIndex(0, l))

    def __customerIDChanged(self):
        c_id = self.ui.fSupplierID.Value()
        if not c_id:
            return
        sql = f'''select fNUIT,fCity,fContato,fAreaCode,
                fCelular,fTelefone,fEndereco,fEmail,
                fWeb,fFax,fNote ,fTaxRegCer
                from t_supplier 
                where fSupplierID={c_id}'''
        dic = JPDb().getDict(sql)[0]
        if self.isNewMode:
            self.ui.fCelular.refreshValueNotRaiseEvent(dic['fCelular'], True)
            self.ui.fContato.refreshValueNotRaiseEvent(dic['fContato'], True)
            self.ui.fTelefone.refreshValueNotRaiseEvent(dic['fTelefone'], True)
        self.ui.fNUIT.setText(dic['fNUIT'])
        self.ui.fCity.setText(dic['fCity'])
        self.ui.fEndereco.setText(dic['fEndereco'])
        self.ui.fEmail.setText(dic['fEmail'])

    def onGetColumnFormulas(self):
        fla = "JPRound(JPRound({3}) * JPRound({4},3),3)"
        return [(5, fla)]

    def __onTaxKeyPress(self, KeyEvent):
        if (KeyEvent.modifiers() == Qt.AltModifier
                and KeyEvent.key() == Qt.Key_Delete):
            self.cacuTax = False
            self.ObjectDict()['fTax'].refreshValueRaiseEvent(None, True)
        elif (KeyEvent.modifiers() == Qt.AltModifier
              and KeyEvent.key() == Qt.Key_T):
            self.cacuTax = True
            self.ObjectDict()['fTax'].refreshValueRaiseEvent(None, True)

    def onGetHiddenColumns(self):
        return [1]

    def onGetReadOnlyColumns(self):
        return [2, 5]

    def onGetColumnWidths(self):
        return [25, 0, 500, 100, 100, 100]

    def onGetFieldsRowSources(self):
        sql = '''select fSupplierName,fSupplierID,
                fNUIT,fCity,fContato,fTaxRegCer from t_supplier'''
        lst_supplier = JPDb().getDataList(sql)
        u_lst = [[item[1], item[0]] for item in JPUser().getAllUserList()]

        return [('fSupplierID', lst_supplier, 1),
                ('fPurchaserID', JPPub().getEnumList(10), 1),
                ('fEntryID', u_lst, 1)]

    def onGetReadOnlyFields(self):
        return ["fEntryID", 'fAmount', 'fPayable', 'fTax', 'fEmail']

    def onGetDisableFields(self):
        return ['fOrderID', 'fCity', 'fNUIT', "fEntryID"]

    def onDateChangeEvent(self, obj, value):

        if not isinstance(obj, QModelIndex):
            if obj.objectName() == "fSupplierID":
                if self.ui.fSupplierID.currentIndex() != -1:
                    self.__customerIDChanged()
                    return

        fAmount = None
        temp_fDesconto = self.ui.fDesconto.Value()
        fDesconto = temp_fDesconto if temp_fDesconto else 0
        fAmount = self.getColumnSum(5)
        if fAmount is None:
            self.ui.fAmount.refreshValueNotRaiseEvent(None, True)
            self.ui.fTax.refreshValueNotRaiseEvent(None, True)
            self.ui.fPayable.refreshValueNotRaiseEvent(None, True)
            return
        else:
            self.ui.fAmount.refreshValueNotRaiseEvent(fAmount, True)

        fTax = 0.0
        if self.cacuTax:
            fTax = JPRound((fAmount - fDesconto) * 0.17, 2)
            self.ui.fTax.refreshValueNotRaiseEvent(fTax, True)
        else:
            fTax = self.ui.fTax.Value()

        fPayable = fAmount + fTax - fDesconto
        self.ui.fPayable.refreshValueNotRaiseEvent(fPayable, True)

    def onAfterSaveData(self, data):
        act = 'new' if self.isNewMode else 'edit'
        JPPub().broadcastMessage(tablename="t_product_warehousereceipt_order",
                                 action=act,
                                 PK=data)
        if self.isNewMode:
            self.ui.fOrderID.refreshValueNotRaiseEvent(data, True)

    def afterSetDataBeforeInsterRowEvent(self, row_data, Index):
        # 用于判断可否有加行
        if row_data is None:
            return False
        if row_data[5] is None:
            return False
        return True
        # data = row_data
        # if data[7] == 0:
        #     return False
        # lt = [data[2], data[4], data[5], data[6], data[7]]
        # lt = [float(str(i)) if i else 0 for i in lt]
        # return int(lt[4] * 100) == int(
        #     reduce(lambda x, y: x * y, lt[0:4]) * 100)

    @pyqtSlot()
    def on_butPrint_clicked(self):
        try:
            rpt = WarehouseReceipt_Bill()
            rpt.getFullProductName = self.getFullProductName

            rpt.PrintCurrentReport(self.ui.fOrderID.Value())
        except Exception as identifier:
            msg = "打印过程出错，错误信息为：{}".format(str(identifier))
            QMessageBox.warning(self, '提示', msg, QMessageBox.Ok,
                                QMessageBox.Ok)

    @pyqtSlot()
    def on_butSave_clicked(self):
        try:
            lst = self.getSqls(self.PKRole)
            isOK, result = JPDb().executeTransaction(lst)
            if isOK:
                self.onAfterSaveData(result)
                try:
                    self.ui.butSave.setEnabled(False)
                    self.ui.butPrint.setEnabled(True)
                    self.ui.butPDF.setEnabled(True)
                except Exception as e:
                    print(str(e))
                self.afterSaveData.emit(result)
                QMessageBox.information(self, '完成',
                                        '保存数据完成！\nSave data complete!')
        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()
