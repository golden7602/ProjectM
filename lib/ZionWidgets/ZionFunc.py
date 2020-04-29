from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from lib.JPMvc.JPFuncForm import JPFunctionForm
from lib.ZionWidgets.Order import EditForm_Order
from lib.ZionWidgets.PrintingOrder import EditForm_PrintingOrder
from lib.ZionWidgets.OutboundOrder import EditForm_OutboundOrder
from PyQt5.QtCore import pyqtSlot, Qt, QModelIndex
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPMvc.JPFuncForm import JPEditFormDataMode
from lib.JPPublc import JPPub


class ZionFuncForm(JPFunctionForm):
    def __init__(self, parent):
        super().__init__(parent)
        self.CP_m_sql = """
                SELECT fOrderID, fOrderDate, fVendedorID, fRequiredDeliveryDate
                    , fCustomerID, fContato, fCelular, fTelefone, fAmount, fTax
                    , fPayable, fDesconto, fNote,fEntryID
                FROM t_order
                WHERE fOrderID = '{}'
                """
        self.CP_s_sql = """
                SELECT fID, fOrderID, fQuant AS '数量Qtd',
                    fProductName AS '名称Descrição',
                    fLength AS '长Comp.', fWidth AS '宽Larg.',
                    fPrice AS '单价P. Unitario', fAmount AS '金额Total'
                FROM t_order_detail
                WHERE fOrderID = '{}'
                """
        self.TP_m_sql = """
            SELECT fOrderID, fCelular, fRequiredDeliveryDate, fContato
                , fTelefone, fVendedorID, fCustomerID, fOrderDate
                , fQuant, fNumerBegin, fNumerEnd
                , fPrice, fLogo, fEspecieID, fAvistaID, fTamanhoID
                , fNrCopyID, fPagePerVolumn, fNote, fAmount, fDesconto
                , fTax, fPayable,fEntryID
            FROM t_order
            WHERE fOrderID = '{}'
            """
        self.OP_m_sql = """
                SELECT fOrderID as 订单号码OrderID
                    , fOrderDate as 日期OrderDate
                    , fVendedorID as 销售人员Vendedor
                    , fRequiredDeliveryDate as 交货日期RequiredDeliveryDate
                    , fCustomerID  as 客户名Cliente
                    , fContato
                    , fCelular
                    , fTelefone
                    , fAmount
                    , fTax
                    , fPayable
                    , fDesconto
                    , fNote
                    ,fEntryID
                FROM t_product_outbound_order
                WHERE fOrderID = '{}'
                """
        self.OP_s_sql = """
                SELECT fID, fOrderID, 
                    fProductID AS '名称Descrição', fQuant AS '数量Qtd',
                    fPrice AS '单价P. Unitario', fAmount AS '金额Total'
                FROM t_product_outbound_order_detail
                WHERE fOrderID = '{}'
                """
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

    def UserSaveData(self, tbName):
        if tbName == 't_order':
            self.refreshListForm()

    def onCurrentRowChanged(self, QModelIndex1, QModelIndex2):
        cur_tp = self.getCurrentSelectPKValue()[0:2]
        if cur_tp == 'CP':
            self.setEditFormSQL(self.CP_m_sql, self.CP_s_sql)
        elif cur_tp == 'TP':
            self.setEditFormSQL(self.TP_m_sql, None)
        elif cur_tp == 'PO':
            self.setEditFormSQL(self.OP_m_sql, self.OP_s_sql)

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        cur_tp = self.getCurrentSelectPKValue()[0:2]
        mycls = {
            'CP': EditForm_Order,
            'TP': EditForm_PrintingOrder,
            'PO': EditForm_OutboundOrder
        }
        C = mycls[cur_tp]
        F = C(sql_main=sql_main,
              edit_mode=edit_mode,
              sql_sub=sql_sub,
              PKValue=PKValue)
        F.OrderType = cur_tp
        if edit_mode != JPEditFormDataMode.ReadOnly:
            F.ui.fCustomerID.setEditable(True)
        F.ui.fOrderID.setEnabled(False)
        F.ui.fCity.setEnabled(False)
        F.ui.fNUIT.setEnabled(False)
        F.ui.fEntryID.setEnabled(False)
        F.ui.fEndereco.setEnabled(False)
        self.onAfterCreatedForm(cur_tp, F)
        return F

    def onAfterCreatedForm(self, cur_tp, form):
        return

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        sql = """
        SELECT fOrderID,
            fQuant AS '数量Qtd',
            fProductName AS '名称Descrição',
            fLength AS '长Comp.', 
            fWidth AS '宽Larg.',
            fPrice AS '单价P. Unitario', 
            fAmount AS '金额Total'
        FROM t_order_detail
        WHERE fOrderID IN (
            SELECT 订单号码OrderID FROM ({cur_sql}) Q)"""
        sql = sql.format(cur_sql=self.currentSQL)
        tab = JPQueryFieldInfo(sql)
        exp = JPExpExcelFromTabelFieldInfo(self.model.TabelFieldInfo,
                                           self.MainForm)
        exp.setSubQueryFieldInfo(tab, 0, 0)
        exp.run()
