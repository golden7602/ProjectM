from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from functools import reduce

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget


from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.JPPublc import JPPub
from lib.JPMvc.JPFuncForm import JPFunctionForm
from lib.ZionWidgets.Order import EditForm_Order
from lib.JPPublc import JPDb

from lib.JPMvc.JPEditFormModel import JPEditFormDataMode
from lib.JPMvc.JPModel import JPTableViewModelReadOnly

from lib.ZionReport.Quotation_Bill import Quotation_Bill

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


class JPFuncForm_Quotation(JPFunctionForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        sql_1 = """
                select 
                    fOrderID as `报价单号OrderID`, 
                    fOrderDate as `报价单日期OrderDate`, 
                    fCustomerName as `客户名Cliente`, 
                    fNUIT as `税号NUIT`, 
                    fCity as `城市City`, 
                    fConfirmed1 as `确认Confirmed`, 
                    fEntry_Name as `录入Entry`, 
                    fConfirm_Name as `fConfirm_Name`, 
                    fAmount as `金额SubTotal`, 
                    fTax as `税金IVA`, 
                    fPayable as `应付金额Valor a Pagar`, 
                    fDesconto as `折扣Desconto`, 
                    fContato as `联系人Contato`, 
                    fCelular as `手机Celular`, 
                    fTelefone as `fTelefone`, 
                    fConfirmed as `已确认Confirmed`, 
                    fCustomerID as `客户编号CustomerID` ,
                    fCreatedOrder
                from v_quotation 
                where  left(fOrderID,2)='QS'
                and fCanceled = 0 
                and fOrderDate{date}
                order by  fOrderID DESC"""
        sql_2 = """
                select 
                    fOrderID as `报价单号OrderID`, 
                    fOrderDate as `报价单日期OrderDate`, 
                    fCustomerName as `客户名Cliente`, 
                    fNUIT as `税号NUIT`, 
                    fCity as `城市City`, 
                    fConfirmed1 as `确认Confirmed`, 
                    fEntry_Name as `录入Entry`, 
                    fConfirm_Name as `fConfirm_Name`, 
                    fAmount as `金额SubTotal`, 
                    fTax as `税金IVA`, 
                    fPayable as `应付金额Valor a Pagar`, 
                    fDesconto as `折扣Desconto`, 
                    fContato as `联系人Contato`, 
                    fCelular as `手机Celular`, 
                    fTelefone as `fTelefone`, 
                    fConfirmed as `已确认Confirmed`, 
                    fCustomerID as `客户编号CustomerID` ,
                    fCreatedOrder
                from v_quotation 
                where  left(fOrderID,2)='QS'
                and fCanceled = 0 
                order by  fOrderID DESC"""
        self.backgroundWhenValueIsTrueFieldName = ['fSubmited']
        self.checkBox_1.setHidden(True)
        self.checkBox_2.setHidden(True)
        super().setListFormSQL(sql_1, sql_2)
        self.tableView.setColumnHidden(16, True)
        self.tableView.setColumnHidden(17, True)
        m_sql = """
                SELECT fOrderID, fOrderDate, fVendedorID, fRequiredDeliveryDate
                    , fCustomerID, fContato, fCelular, fTelefone, fAmount, fTax
                    , fPayable, fDesconto, fNote,fEntryID
                FROM t_quotation
                WHERE fOrderID = '{}'
                """
        s_sql = """
                SELECT fID, fOrderID, fQuant AS '数量Qtd',
                    fProductName AS '名称Descrição',
                    fLength AS '长Comp.', fWidth AS '宽Larg.',
                    fPrice AS '单价P. Unitario', fAmount AS '金额Total'
                FROM t_quotation_detail
                WHERE fOrderID = '{}'
                """
        self.setEditFormSQL(m_sql, s_sql)

    def UserSaveData(self, tbName):
        if tbName == 't_quotation':
            self.refreshListForm()

    def onGetModelClass(self):
        return _myMod

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        frm = Edit_Order_Quotation(sql_main=sql_main,
                                   edit_mode=edit_mode,
                                   sql_sub=sql_sub,
                                   PKValue=PKValue)
        frm.ui.fOrderID.setEnabled(False)
        frm.ui.fCity.setEnabled(False)
        frm.ui.fNUIT.setEnabled(False)
        frm.ui.fEntryID.setEnabled(False)
        frm.ui.fEndereco.setEnabled(False)
        return frm

    @pyqtSlot()
    def on_CmdOrder_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        newPKSQL = JPDb().NewPkSQL(1)
        sql = [
            """
        INSERT INTO t_order (fOrderID, fOrderDate, fVendedorID
            , fRequiredDeliveryDate, fCustomerID
            , fContato, fCelular, fTelefone, fAmount, fTax
            , fPayable, fDesconto, fNote, fEntryID)
            SELECT @PK, fOrderDate, fVendedorID
                , fRequiredDeliveryDate, fCustomerID
                , fContato, fCelular, fTelefone, fAmount, fTax
                , fPayable, fDesconto, fNote, fEntryID
                FROM t_quotation
                WHERE fOrderID = '{id}';""".format(id=cu_id), """
        INSERT INTO t_order_detail (fOrderID, fQuant, fProductName
            , fLength, fWidth, fPrice, fAmount)
            SELECT @PK, fQuant, fProductName, fLength, fWidth
                , fPrice, fAmount
            FROM t_quotation_detail
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


class Edit_Order_Quotation(EditForm_Order):
    def __init__(self, sql_main, sql_sub=None, edit_mode=None, PKValue=None):
        super().__init__(sql_main,
                         sql_sub=sql_sub,
                         edit_mode=edit_mode,
                         PKValue=PKValue)
        self.setPkRole(6)
        self.ui.label_Title_Chn.setText("报价单")
        self.ui.label_Title_Eng.setText("Cotação")
        if self.EditMode != JPEditFormDataMode.ReadOnly:
            self.ui.fCustomerID.setEditable(True)

    @pyqtSlot()
    def on_butPrint_clicked(self):
        rpt = Quotation_Bill()
        rpt.PrintCurrentReport(self.ui.fOrderID.Value())

