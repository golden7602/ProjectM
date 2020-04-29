import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())

from PyQt5.QtCore import QDate, QMetaObject, pyqtSlot, Qt, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog, QItemDelegate)

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPFunction import JPDateConver
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPublc import JPDb, JPPub
from Ui.Ui_FormProductInOutDetail import Ui_Form as Ui_Form_List

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPForms.JPSearch import Form_Search
from lib.ZionWidgets.ViewPic import Form_ViewPic
from lib.JPFunction import GetFileMd5
from lib.ZionReport.ProductInOutDetailsReport import FormReport_ProductInfo_InOutDetail


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_icon = JPPub().MainForm.getIcon('flag_red.png')

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        r = index.row()
        tab = self.TabelFieldInfo
        if role == Qt.DecorationRole and c == 4:
            sl = tab.getOnlyData((r, 4))
            yj = tab.getOnlyData((r, 5))
            sl = sl if sl else 0
            yj = yj if yj else 0
            if sl < yj:
                return self.flag_icon
            else:
                return super().data(index, role)

        return super().data(index, role)


class Form_product_in_out_detail(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        self.list_sql = """
            SELECT q.fProductID as ProductID,
                    p.fProductName AS 产品名称ProductName,
                    sum(rk) AS 入库数量In ,
                    sum(ck) AS 出库数量Out ,
                    p.fCurrentQuantity as 结余库存CurrentQuantity,
                    sum(xsbs) as 销售笔数BillCount
            FROM
                (SELECT d.fProductID,
                    d.fQuant AS rk,
                    null AS ck,
                    null as xsbs,
                    d.TS
                FROM t_product_warehousereceipt_order_detail AS d
                LEFT JOIN t_product_warehousereceipt_order AS o
                    ON d.fOrderID=o.fOrderID
                WHERE o.fOrderDate
                    BETWEEN '{d1}'
                        AND '{d2}'
                        AND o.fSubmited=1
                UNION all
                SELECT d.fProductID,
                    null AS rk,
                    d.fQuant AS ck,
                    1 as xsbs,
                    d.TS
                FROM t_product_outbound_order_detail AS d
                LEFT JOIN t_product_outbound_order AS o
                    ON d.fOrderID=o.fOrderID
                WHERE o.fOrderDate
                    BETWEEN '{d1}'
                        AND '{d2}'
                        AND o.fSubmited=1
                ) AS q
               LEFT JOIN t_product_information as p on q.fProductID=p.fID
            GROUP BY ProductID
            ORDER BY p.fProductName

            """
        self.ui.dateEdit_begin.setDate(
            QDate(QDate.currentDate().year(),
                  QDate.currentDate().month(), 1))
        self.ui.dateEdit_end.setDate(QDate().currentDate())
        self.ui.dateEdit_begin.dateChanged.connect(self.actionClick)
        self.ui.dateEdit_end.dateChanged.connect(self.actionClick)
        self.ui.label.hide()
        self.ui.lineEdit.hide()

        icon = QIcon(JPPub().MainForm.icoPath.format("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        action.triggered.connect(self.actionClick)

    def actionClick(self, where_sql=None):
        d1 = JPDateConver(self.ui.dateEdit_begin.date(), str)
        d2 = JPDateConver(self.ui.dateEdit_end.date(), str)
        tv = self.ui.tableView
        self.dataInfo = JPQueryFieldInfo(self.list_sql.format(d1=d1, d2=d2))
        self.mod = myJPTableViewModelReadOnly(tv, self.dataInfo)
        tv.setModel(self.mod)

        #tv.setItemDelegateForColumn(9, de)
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

    @pyqtSlot()
    def on_CmdPrint_clicked(self):
        d1 = JPDateConver(self.ui.dateEdit_begin.date(), str)
        d2 = JPDateConver(self.ui.dateEdit_end.date(), str)
        if self.list_sql:
            rpt = FormReport_ProductInfo_InOutDetail()
            rpt.sql = self.list_sql.format(d1=d1,d2=d2)
            rpt.beginDate = self.ui.dateEdit_begin.date()
            rpt.endDate = self.ui.dateEdit_end.date()
            rpt.initItem()
            rpt.BeginPrint()