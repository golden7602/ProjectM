from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from functools import reduce

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget
from PyQt5.QtPrintSupport import QPrinter


from lib.JPPublc import JPPub, JPDb
from lib.JPMvc.JPFuncForm import JPFunctionForm
from lib.ZionWidgets.PrintingOrder import EditForm_PrintingOrder

from lib.JPMvc.JPEditFormModel import JPEditFormDataMode
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.ZionReport.PrintingQuotationReport import Order_Printingreport


class _myMod(JPTableViewModelReadOnly):
    def __init__(self, *args):
        super().__init__(*args)
        self.f = QFont()
        self.f.Black = True
        self.f.setBold(True)
        self._getData = self.TabelFieldInfo.getOnlyData

    def data(self, Index, role: int = Qt.DisplayRole):
        if role == Qt.TextColorRole:
            if self._getData([Index.row(), 17]) == 1:
                return QColor(Qt.blue)
        return super().data(Index, role)


class JPFuncForm_PrintingQuotation(JPFunctionForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        sql_1 = """
                select
                    fOrderID as `报价单号fOrderID`,
                    fOrderDate as `报价单日期fOrderDate`,
                    fCustomerName as `客户名Cliente`,
                    fNUIT as `税号NUIT`,
                    fCity as `城市City`,
                    fConfirmed1 as `确认Confirmed`,
                    fEntry_Name as `录入Entry`,
                    fConfirm_Name as `确认人Confirm_Name`,
                    fAmount as `金额SubTotal`,
                    fTax as `税金IVA`,
                    fPayable as `应付金额Valor a Pagar`,
                    fDesconto as `折扣Desconto`,
                    fContato as `联系人Contato`,
                    fCelular as `手机Celular`,
                    fTelefone as `电话Telefone`,
                    fConfirmed as `已确认Confirmed`,
                    fCustomerID as `客户编号CustomerID`,
                    fCreatedOrder
                from v_quotation
                where  left(fOrderID,2)='QP'
                and fCanceled = 0
                and fOrderDate{date}
                order by fOrderID DESC"""
        sql_2 = """
                select
                    fOrderID as `报价单号fOrderID`,
                    fOrderDate as `报价单日期fOrderDate`,
                    fCustomerName as `客户名Cliente`,
                    fNUIT as `税号NUIT`,
                    fCity as `城市City`,
                    fConfirmed1 as `确认Confirmed`,
                    fEntry_Name as `录入Entry`,
                    fConfirm_Name as `确认人Confirm_Name`,
                    fAmount as `金额SubTotal`,
                    fTax as `税金IVA`,
                    fPayable as `应付金额Valor a Pagar`,
                    fDesconto as `折扣Desconto`,
                    fContato as `联系人Contato`,
                    fCelular as `手机Celular`,
                    fTelefone as `电话Telefone`,
                    fConfirmed as `已确认Confirmed`,
                    fCustomerID as `客户编号CustomerID`,
                    fCreatedOrder
                from v_quotation
                where  left(fOrderID,2)='QP'
                and fCanceled = 0
                order by  fOrderID DESC"""
        self.backgroundWhenValueIsTrueFieldName = ['fSubmited']
        self.checkBox_1.setHidden(True)
        self.checkBox_2.setHidden(True)
        super().setListFormSQL(sql_1, sql_2)
        self.tableView.setColumnHidden(16, True)
        self.tableView.setColumnHidden(17, True)
        m_sql = """
                SELECT fOrderID, fCelular, fRequiredDeliveryDate, fContato
                    , fTelefone, fVendedorID, fCustomerID, fOrderDate
                    , fQuant, fNumerBegin, fNumerEnd
                    , fPrice, fLogo, fEspecieID, fAvistaID, fTamanhoID
                    , fNrCopyID, fPagePerVolumn, fNote, fAmount, fDesconto
                    , fTax, fPayable,fEntryID
                FROM t_quotation
                WHERE fOrderID = '{}'
                """
        self.setEditFormSQL(m_sql, None)

    def UserSaveData(self, tbName):
        if tbName == 't_quotation':
            self.refreshListForm()

    def onGetModelClass(self):
        return _myMod

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        return Edit_PrintingQuotation(sql_main=sql_main,
                                      edit_mode=edit_mode,
                                      sql_sub=sql_sub,
                                      PKValue=PKValue)

    @pyqtSlot()
    def on_CmdOrder_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        newPKSQL = JPDb().NewPkSQL(5)
        sql = [
            """
        INSERT INTO t_order (fOrderID, fCelular, fRequiredDeliveryDate, fContato
                    , fTelefone, fVendedorID, fCustomerID, fOrderDate
                    , fQuant, fNumerBegin, fNumerEnd
                    , fPrice, fLogo, fEspecieID, fAvistaID, fTamanhoID
                    , fNrCopyID, fPagePerVolumn, fNote, fAmount, fDesconto
                    , fTax, fPayable,fEntryID)
            SELECT @PK, fCelular, fRequiredDeliveryDate, fContato
                        , fTelefone, fVendedorID, fCustomerID, fOrderDate
                        , fQuant, fNumerBegin, fNumerEnd
                        , fPrice, fLogo, fEspecieID, fAvistaID, fTamanhoID
                        , fNrCopyID, fPagePerVolumn, fNote, fAmount, fDesconto
                        , fTax, fPayable,fEntryID
            FROM t_quotation
            WHERE fOrderID = '{id}';""".format(id=cu_id), """
        UPDATE t_quotation SET fCreatedOrder=1 WHERE fOrderID = '{id}';
        """.format(id=cu_id)
        ]
        sql = newPKSQL[0:2] + sql + newPKSQL[2:]
        for q in sql:
            print(q)
        try:
            isOK, result = JPDb().executeTransaction(sql)
            if isOK:
                info = '已经根据报价单生成了订单【{id}】，请修改此订单信息!\n'
                info = info + 'The order [{id}] has been generated according '
                info = info + 'to the quotation. Please modify the order information.'
                QMessageBox.information(self, "提示", info.format(id=result))
                JPPub().broadcastMessage(tablename="t_order",
                                         action='createOrder',
                                         PK=data)
                self.refreshListForm()
        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()


class Edit_PrintingQuotation(EditForm_PrintingOrder):
    def __init__(self, sql_main, sql_sub=None, edit_mode=None, PKValue=None):
        super().__init__(sql_main,
                         sql_sub=sql_sub,
                         edit_mode=edit_mode,
                         PKValue=PKValue)
        self.setPkRole(4)
        self.ui.label_Title_Chn.setText("报价单")
        self.ui.label_Title_Eng.setText("Cotação")
        if self.EditMode != JPEditFormDataMode.ReadOnly:
            self.ui.fCustomerID.setEditable(True)

    @pyqtSlot()
    def on_butPrint_clicked(self):
        rpt = Order_Printingreport()
        rpt.PrintCurrentReport(self.ui.fOrderID.Value())
