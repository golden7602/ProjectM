from functools import reduce
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPMvc.JPEditFormModel import JPFormModelMain, JPFormModelMainHasSub
from lib.JPMvc.JPFuncForm import JPFunctionForm
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.JPPublc import JPDb, JPPub, JPUser
from lib.ZionWidgets.EditFormOrderOrPrintingOrder import (JPFormOrder,
                                                          JPFormPrintingOrder)
from lib.ZionWidgets.ZionFunc import ZionFuncForm


class _myMod(JPTableViewModelReadOnly):
    def __init__(self, *args):
        super().__init__(*args)
        self.viewed_icon = JPPub().MainForm.getIcon('watch_variable.ico')
        self.ok_icon = JPPub().MainForm.getIcon('delivery.png')
        self._getData = self.TabelFieldInfo.getOnlyData

    def data(self, index, role: int = Qt.DisplayRole):
        r = index.row()
        c = index.column()
        if role == Qt.DecorationRole:
            if c == 11 and self._getData((r, 12)):
                return self.viewed_icon
            elif c == 3 and self._getData((r, 5)):
                return self.ok_icon
            return super().data(index, role)
        elif role == Qt.TextAlignmentRole and (c == 3 or c == 11):
            return Qt.AlignCenter
        return super().data(index, role)


class _myFuncForm(JPFunctionForm):
    def __init__(self, parent):
        super().__init__(parent)
        self.CP_m_sql = """
                SELECT fOrderID, fOrderDate, fVendedorID, fRequiredDeliveryDate
                    , fCustomerID, fNote,fEntryID
                    , fContato, fCelular  ,fTelefone
                    , fNUIT, fCity, fEndereco
                    ,' ' as fAmount,' ' as fDesconto,' ' as fTax,' ' as fPayable, ' ' as fPrice
                FROM v_order_readonly
                WHERE fOrderID = '{}'
                """
        self.CP_s_sql = """
                SELECT fID, fQuant AS '数量Qtd',
                    fProductName AS '名称Descrição',
                    fLength AS '长Comp.', fWidth AS '宽Larg.'
                FROM t_order_detail
                WHERE fOrderID = '{}'
                """
        self.TP_m_sql = """
                SELECT fOrderID, fRequiredDeliveryDate, fVendedorID
                    , fCustomerID, fOrderDate
                    , fQuant, fNumerBegin, fNumerEnd, fPrice
                    , fLogo, fEspecieID, fAvistaID, fTamanhoID, fNrCopyID
                    , fPagePerVolumn, fNote, fEntryID, fContato, fCelular
                    , fTelefone, fNUIT, fCity, fEndereco
                    ,' ' as fAmount,' ' as fDesconto,' ' as fTax,' ' as fPayable, ' ' as fPrice
                FROM v_order_readonly
                WHERE fOrderID = '{}'
            """

    def onCurrentRowChanged(self, QModelIndex1, QModelIndex2):
        cur_tp = self.getCurrentSelectPKValue()[0:2]
        if cur_tp == 'CP':
            self.setEditFormSQL(self.CP_m_sql, self.CP_s_sql)
        elif cur_tp == 'TP':
            self.setEditFormSQL(self.TP_m_sql, None)


class JPFuncForm_Complete(_myFuncForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        sql_0 = """
                SELECT fOrderID as `订单号码OrderID`,
                    fOrderDate as `日期OrderDate`,
                    fCustomerName as `客户名Cliente`,
                    fDelivered1 as `已完成fDelivered1`,
                    fDeliverer_Name as `fDeliverer`,
                    fDelivered as `已完成fDelivered`,
                    fCity as `城市City`,
                    fEndereco as `fEndereco`,
                    fContato as `联系人Contato`,
                    fCelular as `手机Celular`,
                    fTelefone as `电话fTelefone`,
                    fDeliverViewed1 as `已查阅Viewed1`,
                    fDeliverViewed as `已查阅Viewed`
                FROM v_order AS o """
        sql_1 = sql_0 + """
                WHERE fConfirmed=1 AND fCanceled=0 And fOrderDate{date}
                        AND (fDelivered={ch1} OR fDelivered={ch2})
                ORDER BY  forderID DESC"""

        sql_2 = sql_0 + """
                WHERE fConfirmed=1 AND fCanceled=0
                ORDER BY  forderID DESC"""

        self.backgroundWhenValueIsTrueFieldName = ['fSubmited']
        self.checkBox_1.setText('finished')
        self.checkBox_2.setText('UnCompleted')
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(True)
        self.ui.comboBox.setCurrentIndex(1)
        self.setListFormSQL(sql_1, sql_2)
        self.tableView.setColumnHidden(5, True)
        self.tableView.setColumnHidden(12, True)

    def onGetModelClass(self):
        return _myMod

    @pyqtSlot()
    def on_CmdBrowse_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        sql = "update t_order set fDeliverViewed=1 where fOrderID='{}'"
        db = JPDb()
        db.executeTransaction(sql.format(cu_id))
        super().on_CmdBrowse_clicked()
        self.refreshListForm()

    @pyqtSlot()
    def on_CmdComplete_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        sql = "update t_order set fDeliverViewed=1,fDelivered=1,"
        sql = sql + "fDelivererID={uid} where fOrderID='{pk}'"
        db = JPDb()
        us = JPUser()
        sql = sql.format(pk=cu_id, uid=us.currentUserID())
        msg = '确认要交付记录【{cu_id}】吗？\n'
        msg = msg + 'Are you sure you want to deliver this order[{cu_id}]?'
        msg = msg.format(cu_id=cu_id)
        if QMessageBox.question(JPPub().MainForm, '确认', msg,
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) == QMessageBox.Yes:
            db.executeTransaction(sql)
            self.refreshListForm()

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        cur_tp = self.getCurrentSelectPKValue()[0:2]
        mycls = {'CP': EditForm_Order, 'TP': EditForm_PrintingOrder}
        C = mycls[cur_tp]
        F = C(sql_main=sql_main,
              edit_mode=edit_mode,
              sql_sub=sql_sub,
              PKValue=PKValue)
        # self.onAfterCreatedForm(cur_tp, F)
        return F

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        if self.model.rowCount() == 0:
            return
        exp = JPExpExcelFromTabelFieldInfo(self.model.TabelFieldInfo,
                                           self.MainForm)
        exp.run()


def hideObject(ui):
    ui.butSave.hide()
    ui.butPrint.hide()
    ui.butPDF.hide()


class EditForm_Order(JPFormModelMainHasSub):
    def __init__(self,
                 sql_main,
                 PKValue,
                 sql_sub,
                 edit_mode,
                 flags=Qt.WindowFlags()):
        super().__init__(JPFormOrder(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         sql_sub=sql_sub,
                         edit_mode=edit_mode,
                         flags=flags)
        self.setPkRole(1)
        self.ui.label_logo.setPixmap(QPixmap(getcwd() +
                                             "\\res\\tmLogo100.png"))
        hideObject(self.ui)
        self.readData()

    def onGetFieldsRowSources(self):
        pub = JPPub()
        u_lst = [[item[1], item[0]] for item in JPUser().getAllUserList()]
        return [('fCustomerID', pub.getCustomerList(), 1),
                ('fVendedorID', pub.getEnumList(10), 1),
                ('fEntryID', u_lst, 1)]

    def onGetColumnWidths(self):
        return [0, 60, 300, 100, 100]


class EditForm_PrintingOrder(JPFormModelMain):
    def __init__(self, sql_main, sql_sub=None, edit_mode=None, PKValue=None):
        super().__init__(JPFormPrintingOrder(),
                         sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode)
        pix = QPixmap(getcwd() + "\\res\\tmLogo100.png")
        self.ui.label_logo.setPixmap(pix)
        hideObject(self.ui)
        self.readData()

    def onGetFieldsRowSources(self):
        pub = JPPub()
        u_lst = [[item[1], item[0]] for item in JPUser().getAllUserList()]
        return [('fCustomerID', pub.getCustomerList(), 1),
                ('fVendedorID', pub.getEnumList(10), 1),
                ('fEspecieID', pub.getEnumList(2), 1),
                ('fAvistaID', pub.getEnumList(7), 1),
                ('fTamanhoID', pub.getEnumList(8), 1),
                ('fNrCopyID', pub.getEnumList(9), 1), ('fEntryID', u_lst, 1)]
