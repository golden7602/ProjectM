from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import QDate, QMetaObject, QModelIndex, Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import (QAction, QLineEdit, QMessageBox, QPushButton,
                             QWidget)

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPFunction import JPDateConver
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPPublc import JPDb, JPPub
from Ui.Ui_FormCustomer_Arrears import Ui_Form as Ui_Form_List


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, tableView, tabelFieldInfo):
        super().__init__(tableView, tabelFieldInfo)

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        r = index.row()
        if c == 1 and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif r == 0 and role == Qt.TextColorRole:
            return QColor(Qt.blue)
        else:
            return super().data(index, role)


class Form_FormCustomer_Arrears(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)

        icon = QIcon(JPPub().MainForm.icoPath.format("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        action.triggered.connect(self.actionClick)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.mod_rec = None
        self.mod_order = None
        mainform.addOneButtonIcon(self.ui.CmdPrint_BillDetail, 'print.png')
        mainform.addOneButtonIcon(self.ui.CmdExportExcel_BillDetail,
                                  'exportToexcel.png')
        mainform.addOneButtonIcon(self.ui.CmdPrint_RecDetail, 'print.png')
        mainform.addOneButtonIcon(self.ui.CmdExportExcel_RecDetail,
                                  'exportToexcel.png')

        self.ui.CmdExportExcel_BillDetail.clicked.connect(
            self.on_CmdExportExcel_BillDetail_clicked)
        self.ui.CmdExportExcel_RecDetail.clicked.connect(
            self.on_CmdExportExcel_RecDetail_clicked)

        self.actionClick()

    def actionClick(self):
        sql = """
            SELECT c.fCustomerID AS `ID`, c.fCustomerName AS `客户名称Cliente`, c.fNUIT AS `税号NUIT`, c.fCity AS `城市City`
                , if(isnull(QDD.dd), NULL, QDD.dd) AS 订单应付金额OrderPayable
                , if(isnull(QSK.sk), NULL, QSK.sk) AS Aeceivables收款
                , if(if(isnull(QDD.dd), 0, QDD.dd) - if(isnull(QSK.sk), 0, QSK.sk) = 0, NULL, if(isnull(QDD.dd), 0, QDD.dd) - if(isnull(QSK.sk), 0, QSK.sk)) AS Arrears欠款
            FROM t_customer c
                LEFT JOIN (
                    SELECT fCustomerID, SUM(fAmountCollected) AS sk
                    FROM t_receivables
                    GROUP BY fCustomerID
                ) QSK
                ON QSK.fCustomerID = c.fCustomerID
                LEFT JOIN (
                    SELECT fCustomerID, SUM(fPayable) AS dd
                    FROM v_all_sales as Q_1
                    GROUP BY fCustomerID
                ) QDD
                ON QDD.fCustomerID = c.fCustomerID
            WHERE NOT (isnull(QDD.dd)
            AND isnull(QSK.sk)) AND {wherestring}"""
        wherestring = """(
            fCustomerName like '%{key}%' or
            fNUIT like '%{key}%'
        )"""
        txt = self.ui.lineEdit.text()
        txt = txt if txt else ''
        wherestring = wherestring.format(key=txt)
        sql = sql.format(wherestring=wherestring)

        tv = self.ui.tableView
        self.dataInfo = JPQueryFieldInfo(sql)
        self.mod = JPTableViewModelReadOnly(tv, self.dataInfo)
        tv.setModel(self.mod)
        tv.resizeColumnsToContents()

        tv.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(self.refreshRec)
        tv.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(
            self.refreshOrder)

    def __getUID(self):
        r = self.ui.tableView.currentIndex()
        if r:
            return self.dataInfo.DataRows[r.row()].Datas[0]
        else:
            return -1

    def refreshOrder(self):
        sql = """
            SELECT * 
            FROM   (SELECT forderid   AS 订单号码OrderID, 
                        forderdate AS 日期OrderDate, 
                        fprice     AS '单价P. Unitario', 
                        fquant     AS '数量Qtd', 
                        famount    AS 金额SubTotal, 
                        fdesconto  AS 折扣Desconto, 
                        ftax       AS 税金IVA, 
                        fpayable   AS `应付金额Valor a Pagar` 
                    FROM   v_all_sales 
                    WHERE  fcustomerid = {uid} 
                        
                    UNION ALL 
                    SELECT ''             AS 订单号码OrderID, 
                        '合计Sum'    AS 日期OrderDate, 
                        ''             AS '单价P. Unitario', 
                        ''             AS '数量Qtd', 
                        Sum(famount)   AS 金额SubTotal, 
                        Sum(fdesconto) AS 折扣Desconto, 
                        Sum(ftax)      AS 税金IVA, 
                        Sum(fpayable)  AS `应付金额Valor a Pagar` 
                    FROM   v_all_sales 
                    WHERE  fcustomerid = {uid}
                        ) AS Q1 
            ORDER  BY Q1.日期orderdate DESC 
        """
        tv = self.ui.tableView_order
        sql = sql.format(uid=self.__getUID())
        self.dataInfo_order = JPQueryFieldInfo(sql)
        self.mod_order = myJPTableViewModelReadOnly(tv, self.dataInfo_order)
        tv.setModel(self.mod_order)
        tv.resizeColumnsToContents()

    def refreshRec(self):
        sql = """SELECT * 
                    FROM   (SELECT fid              AS 流水号ID, 
                                freceiptdate     AS 收款日期ReceiptDate, 
                                e.ftitle         AS 收款方式ModoPago, 
                                famountcollected AS 收款额AmountCollected, 
                                u.fusername      AS 收款人fPayee 
                            FROM   t_receivables r 
                                LEFT JOIN t_enumeration e 
                                        ON r.fpaymentmethodid = e.fitemid 
                                LEFT JOIN sysusers u 
                                        ON r.fpayeeid = u.fuserid 
                            WHERE  r.fcustomerid = {uid} 
                            UNION ALL 
                            SELECT ''                    AS 流水号ID, 
                                '合计Sum'           AS 收款日期ReceiptDate, 
                                ''                    AS 收款方式ModoPago, 
                                Sum(famountcollected) AS 收款额AmountCollected, 
                                ''                    AS 收款人fPayee 
                            FROM   t_receivables r 
                            WHERE  r.fcustomerid = {uid}) Q1 
                    ORDER  BY Q1.收款日期receiptdate DESC """
        tv = self.ui.tableView_rec
        sql = sql.format(uid=self.__getUID())
        self.dataInfo_rec = JPQueryFieldInfo(sql)
        self.mod_rec = myJPTableViewModelReadOnly(tv, self.dataInfo_rec)
        tv.setModel(self.mod_rec)
        tv.resizeColumnsToContents()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.mod.TabelFieldInfo,
                                           JPPub().MainForm)
        exp.run()


    def on_CmdExportExcel_BillDetail_clicked(self):
        if self.mod_order:
            exp = JPExpExcelFromTabelFieldInfo(self.mod_order.TabelFieldInfo,
                                               self.MainForm)
            exp.run()

    def on_CmdExportExcel_RecDetail_clicked(self):
        if self.mod_rec:
            exp = JPExpExcelFromTabelFieldInfo(self.mod_rec.TabelFieldInfo,
                                               self.MainForm)
            exp.run()
