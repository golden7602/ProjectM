from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from functools import reduce

from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget
from PyQt5.QtPrintSupport import QPrinter

from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.JPPublc import JPPub, JPDb
from lib.ZionWidgets.ZionFunc import ZionFuncForm
from lib.JPMvc.JPModel import JPTableViewModelReadOnly


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ok_icon = JPPub().MainForm.getIcon('yes.ico')
        self.cancel_icon = JPPub().MainForm.getIcon('cancel.ico')
        self.delivery_icon = JPPub().MainForm.getIcon('delivery.png')

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        r = index.row()
        tab = self.TabelFieldInfo
        if c in (3, 5, 7, 9) and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DecorationRole:
            if c == 3 and tab.getOnlyData((r, 3)):
                return self.cancel_icon
            if c == 5 and tab.getOnlyData((r, 5)):
                return self.ok_icon
            if c == 7 and tab.getOnlyData((r, 7)):
                return self.ok_icon
            if c == 9 and tab.getOnlyData((r, 9)):
                return self.delivery_icon
        return super().data(index, role)


class JPFuncForm_Adjustment(ZionFuncForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        sql_1 = """
                SELECT fOrderID as `订单号码OrderID`,
                    fOrderDate as `日期OrderDate`,
                    fCustomerName as `客户名Cliente`,
                    fCanceled1 as `已作废Canceled`,
                    fCancel_Name as `作废提交人CancelUser`,
                    fSubmited1 as `提交Submited`,
                    fSubmit_Name as `提交人Submit_User`,
                    fConfirmed1 as `确认Confirmed`,
                    fConfirm_Name as `确认人fConfirm_Name`,
                    fDelivered1 as `交付Delivered`,
                    fDeliverer_Name as `交付人Deliverer_Name`,
                    fAmount as `金额SubTotal`,
                    fTax as `税金IVA`,
                    fPayable as `应付金额Valor a Pagar`,
                    fDesconto as `折扣Desconto`,
                    fCustomerID as `客户编号CustomerID`,
                    fCanceled as `作废fCanceled`
                FROM v_order AS o
                WHERE fOrderDate{date}
                        AND (fCanceled={ch1} OR fCanceled={ch2})
                ORDER BY  forderID DESC"""

        sql_2 = """
                SELECT fOrderID as `订单号码OrderID`,
                    fOrderDate as `日期OrderDate`,
                    fCustomerName as `客户名Cliente`,
                    fCanceled1 as `已作废Canceled`,
                    fCancel_Name as `作废提交人CancelUser`,
                    fSubmited1 as `提交Submited`,
                    fSubmit_Name as `Submit_User`,
                    fConfirmed1 as `确认Confirmed`,
                    fConfirm_Name as `确认人fConfirm_Name`,
                    fDelivered1 as `交付Delivered`,
                    fDeliverer_Name as `交付人Deliverer_Name`,
                    fAmount as `金额SubTotal`,
                    fTax as `税金IVA`,
                    fPayable as `应付金额Valor a Pagar`,
                    fDesconto as `折扣Desconto`,
                    fCustomerID as `客户编号CustomerID`,
                    fCanceled as `fCanceled`
                FROM v_order AS o
                ORDER BY  forderID DESC"""

        self.backgroundWhenValueIsTrueFieldName = ['fCanceled']
        self.checkBox_1.setText('Cancelled')
        self.checkBox_2.setText('Normal')
        self.checkBox_1.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.ui.comboBox.setCurrentIndex(1)
        self.setListFormSQL(sql_1, sql_2)
        self.tableView.setColumnHidden(13, True)
        self.tableView.setColumnHidden(15, True)
        self.tableView.setColumnHidden(16, True)

    def onGetModelClass(self):
        return myJPTableViewModelReadOnly

    @pyqtSlot()
    def on_CmdCancel_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        sql = "update t_order set fCanceled=1 where fOrderID='{pk}'"
        db = JPDb()
        sql = sql.format(pk=cu_id)
        msg = '您确认要作废此订单？\n'
        msg = msg + "Are you sure you want to cancel this order?"
        msg = msg.format(pk=cu_id)
        if QMessageBox.question(JPPub().MainForm, '确认', msg,
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) == QMessageBox.Yes:
            db.executeTransaction(sql)
            self.refreshListForm()

    @pyqtSlot()
    def on_CmdAdjustment_clicked(self):
        super().on_CmdEdit_clicked()

    def onAfterCreatedForm(self, cur_tp, form):
        if form.OrderType == "CP":
            form.setWindowTitle("Order Adjustment")
            form.ui.fOrderID.setEnabled(False)
            form.ui.fCelular.setEnabled(False)
            form.ui.fRequiredDeliveryDate.setEnabled(True)
            form.ui.fContato.setEnabled(False)
            form.ui.fTelefone.setEnabled(False)
            form.ui.fCustomerID.setEnabled(True)
            form.ui.fOrderDate.setEnabled(True)
            form.ui.fVendedorID.setEnabled(True)
            form.ui.fEntryID.setEnabled(False)
            form.ui.fNote.setEnabled(True)
            form.ui.fAmount.setEnabled(False)
            form.ui.fDesconto.setEnabled(True)
            form.ui.fTax.setEnabled(True)
            form.ui.fPayable.setEnabled(False)

        if form.OrderType == "TP":
            form.setWindowTitle("PrintingOrder Adjustment")
            for nm in form.ObjectDict().keys():
                form.ObjectDict()[nm].setEnabled(False)
            form.ui.fPrice.setEnabled(True)
            form.ui.fTax.setEnabled(True)
        #self.__setFormBack(form)
        return super().onAfterCreatedForm(cur_tp, form)

    # def __setFormBack(self,form):
    #     pk = form.ui.fOrderID.text()
    #     sql = f"select fCanceled from t_order where fOrderID='{pk}'"
    #     db=JPDb()
    #     result=db.executeTransaction(sql)
    #     if result:
    #         form.setAutoFillBackground(True)
    #         palette1 = QPalette()
    #         palette1.setColor(self.backgroundRole(), QColor(255, 192, 203))
    #         #palette1.setBrush(form.backgroundRole(), QBrush(JPPub().MainForm.getPixmap('cancel.png')))
    #         form.setPalette(palette1)
