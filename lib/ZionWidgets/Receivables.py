from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import QDate, QMetaObject, QModelIndex, Qt, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QPushButton, QWidget

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromManyTabelFieldInfo
from lib.JPFunction import JPDateConver, JPGetDisplayText, findButtonAndSetIcon
from lib.JPMvc import JPWidgets
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPMvc.JPModel import JPTableViewModelReadOnly

from lib.JPPublc import JPPub, JPUser
from Ui.Ui_FormReceivableEdit import Ui_Form as Edit_ui
from Ui.Ui_FormReceivables import Ui_Form
from lib.ZionReport.Receivables_Report import FormReport_Rec_print


class Form_Receivables(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.MainForm = mainform
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        #findButtonAndSetIcon(self)
        mainform.addForm(self)
        self.SQLCustomerArrearsList = """
            select c.fCustomerID as 客户编号ID,
                c.fCustomerName as `客户名Cliente`,
                c.fCity as 城市City,
            if(	YS.fYS=0,null,YS.fYS) as `应收合计TotalReceivables`,
                if(SK.fSK=0,null,SK.fSK) as `收款累计SumRec`,
                if(if(isnull(YS.fYS),0,YS.fYS)-if(isnull(SK.fSK),0,SK.fSK)=0,null,if(isnull(YS.fYS),0,YS.fYS)-if(isnull(SK.fSK),0,SK.fSK)) as `欠款Arrears`,
                r1.fReceiptDate as `最后收款日LastfReceiptDate`,
                cast(r1.fAmountCollected as DECIMAL) as `最后收款额LastAmountCollected`
            from t_customer as c left join 
                (select o.fCustomerID,
                    cast(sum(o.fPayable) as DECIMAL) as fYS 
                    from v_all_sales as o 
                    group by o.fCustomerID) as YS
            on c.fCustomerID=YS.fCustomerID left join 
                (select r.fCustomerID,
                    cast(sum(r.fAmountCollected) as DECIMAL) as fSK,
                    max(r.fID) as LastRecID 
                    from t_receivables as r 
                    group by r.fCustomerID ) as SK
                on c.fCustomerID=SK.fCustomerID
                left join t_receivables as r1 
                on r1.fID=SK.LastRecID
            where c.fCustomerID={CustomerID}
        """
        self.SQLCustomerRecorder = """
                select 
                Q.fDate as 日期OrderDate, 
                Q.fOrderID as 订单号码OrderID, 
                Q.fPayable as 应收金额Payable, 
                Q.fAmountCollected as 收款fAmountCollected 
                from 
                (
                    select 
                    o.fOrderDate as fDate, 
                    o.fOrderID, 
                    cast(o.fPayable as DECIMAL) as fPayable, 
                    null as fAmountCollected, 
                    o.ts 
                    from 
                    v_all_sales as o 
                    where 
                    o.fCustomerID ={CustomerID} 
                    union all 
                    select 
                    r.fReceiptDate as fDate, 
                    Null as fOrderID, 
                    Null as fPayable, 
                    cast(r.fAmountCollected as DECIMAL) as fAmountCollected, 
                    r.ts 
                    from 
                    t_receivables as r 
                    where 
                    r.fCustomerID ={CustomerID} 
                    union all 
                    select 
                    null as fDate, 
                    'Sum' as fOrderID, 
                    cast(
                        sum(Q1.fPayable) as DECIMAL
                    ) as fPayable, 
                    cast(
                        sum(Q1.fAmountCollected) as DECIMAL
                    ) as fAmountCollected, 
                    null as ts 
                    from 
                    (
                        select 
                        o.fOrderDate as fDate, 
                        o.fOrderID, 
                        cast(o.fPayable as DECIMAL) as fPayable, 
                        null as fAmountCollected, 
                        o.ts 
                        from 
                        v_all_sales as o 
                        where 
                        o.fCustomerID ={CustomerID} 
                        union all 
                        select 
                        r.fReceiptDate as fDate, 
                        Null as fOrderID, 
                        Null as fPayable, 
                        cast(r.fAmountCollected as DECIMAL), 
                        r.ts 
                        from 
                        t_receivables as r 
                        where 
                        r.fCustomerID ={CustomerID}
                    ) as Q1
                ) as Q 
                order by 
                Q.TS DESC
        """
        self.SQLCurrentDayRec = """
            SELECT fID as 流水号ID,
                    fCustomerID as 客户编号CustomerID,
                    fCustomerName as 客户名Cliente,
                    fReceiptDate as 收款日期ReceiptDate,
                    fAmountCollected as 收款额AmountCollected,
                    fPayee as 收款人fPayee,
                    fPaymentMethod AS 收款方式ModoPago,
                    fOrderID as 订单号OrderID,
                    fNote as 备注Note
                    
            FROM v_receivables as r           
            WHERE 
                r.fReceiptDate = STR_TO_DATE('{dateString}', '%Y-%m-%d') 
            order by fID DESC
        """
        self.SQLSumPaymentMethod = """
            SELECT e.fTitle AS `收款方式PaymentMethod` ,
                    sum(fAmountCollected) AS `收款合计Collection of receipts`,
                    count(fID) AS `收款笔数Number of Payments Received`
            FROM t_receivables AS r
            LEFT JOIN t_enumeration AS e
                ON r.fPaymentMethodID=e.fItemID
            WHERE 
                r.fReceiptDate = STR_TO_DATE('{dateString}', '%Y-%m-%d') 
            GROUP BY  r.fPaymentMethodID

            """
        self.ui.SelectDate.dateChanged.connect(self.dateChanged)
        # 引发一次日期修改事件，刷新 左上、右上
        self.ui.SelectDate.setDate(QDate.currentDate())
        # 引发一次事件，刷新左下、右下
        self.currentCustomerChanged()
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)
        self.MsgWindowsPoped = False

    def UserSaveData(self, tbName):
        if self.MsgWindowsPoped:
            return
        else:
            self.MsgWindowsPoped = True
        msg = "其他用户添加了新的收款记录，是否刷新窗口?"
        msg = msg + '\nOther users have added new receipt records. Do you refresh the window?'
        if tbName == 't_receivables':
            if QMessageBox.question(self, "确认", msg, QMessageBox.Ok
                                    | QMessageBox.Cancel) == QMessageBox.Ok:
                self.dateChanged(self.ui.SelectDate.date())
                self.currentCustomerChanged()
            self.MsgWindowsPoped = False

    def __formChange(self, *args):
        print(args)

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        frm = RecibidoEdit()
        frm.ListForm = self
        frm.ui.fAmountCollected.setDoubleValidator(-100000000.0, 100000000.0,
                                                   2)
        frm._currentDate = self.ui.SelectDate.date()
        frm.exec_()

    @pyqtSlot()
    def on_CmdRecibido_clicked(self):
        frm = RecibidoEdit()
        frm.ListForm = self
        frm.ui.fAmountCollected.setDoubleValidator(0.01, 100000000.0, 2)
        frm._currentDate = self.ui.SelectDate.date()
        #frm.ui.fNote.refreshValueNotRaiseEvent('DIBOTO', True)
        frm.exec_()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromManyTabelFieldInfo(
            self.tabinfoCurrentDayRec,
            self.tabinfoFangShiTongJi,
            self.tableinfoCustomerRecorder,
            self.tableinfoCustomerArrearsList,
            MainForm=self.MainForm)
        exp.run()

    @pyqtSlot()
    def on_CmdDailyRreport_clicked(self):
        if len(self.tabinfoCurrentDayRec) == 0:
            return
        try:
            p = FormReport_Rec_print(
                JPDateConver(self.ui.SelectDate.date(), str),
                self.tabinfoCurrentDayRec, self.tabinfoFangShiTongJi,
                JPDateConver(self.ui.SelectDate.date(), str))
            p.BeginPrint()
        except Exception as e:
            print(e)
            pass

    def dateChanged(self, s_data):
        str_date = JPDateConver(self.ui.SelectDate.date(), str)

        # 设置当前日收款记录（左上）
        sql = self.SQLCurrentDayRec.format(dateString=str_date)
        self.tabinfoCurrentDayRec = JPQueryFieldInfo(sql)
        self.modCurrentDayRec = JPTableViewModelReadOnly(
            self.ui.tabCurrentDayRec, self.tabinfoCurrentDayRec)
        self.ui.tabCurrentDayRec.setModel(self.modCurrentDayRec)
        self.ui.tabCurrentDayRec.resizeColumnsToContents()
        self.ui.tabCurrentDayRec.selectionModel(
        ).currentRowChanged[QModelIndex, QModelIndex].connect(
            self.currentCustomerChanged)

        # 设置当前日收款方式统计（右上）
        self.tabinfoFangShiTongJi = JPQueryFieldInfo(
            self.SQLSumPaymentMethod.format(dateString=str_date))
        self.modFangShiTongJi = JPTableViewModelReadOnly(
            self.ui.SumPaymentMethod, self.tabinfoFangShiTongJi)
        self.ui.SumPaymentMethod.setModel(self.modFangShiTongJi)
        self.ui.SumPaymentMethod.resizeColumnsToContents()

        #self.currentCustomerChanged()

    def currentCustomerChanged(self):
        id = -1
        index = self.ui.tabCurrentDayRec.selectionModel().currentIndex()
        if index.isValid():
            id = self.modCurrentDayRec.TabelFieldInfo.getOnlyData(
                [index.row(), 1])
        # 刷新左下
        self.tableinfoCustomerRecorder = JPQueryFieldInfo(
            self.SQLCustomerRecorder.format(CustomerID=id))
        self.modCustomerRecorder = JPTableViewModelReadOnly(
            self.ui.tabCustomerRecorder, self.tableinfoCustomerRecorder)
        self.ui.tabCustomerRecorder.setModel(self.modCustomerRecorder)
        self.ui.tabCustomerRecorder.resizeColumnsToContents()

        # 刷新右下
        self.tableinfoCustomerArrearsList = JPQueryFieldInfo(
            self.SQLCustomerArrearsList.format(CustomerID=id))
        self.modCustomerArrearsList = JPTableViewModelReadOnly(
            self.ui.tabCustomerArrearsList, self.tableinfoCustomerArrearsList)
        self.ui.tabCustomerArrearsList.setModel(self.modCustomerArrearsList)
        self.ui.tabCustomerArrearsList.resizeColumnsToContents()

        # self.ui.tabCurrentDayRec.setModel(self.modCurrentDayRec)
        # self.ui.tabCurrentDayRec.resizeColumnsToContents()


class RecibidoEdit(JPFormModelMain):
    def __init__(self):
        m_sql = '''SELECT fID, 
                        fCustomerID AS 客户名Cliente, 
                        fPaymentMethodID AS 收款方式ModoPago, 
                        fReceiptDate as 收款日期ReceiptDate,
                        fAmountCollected AS 金额Amount,
                        fPayeeID, fNote,
                        fOrderID as 单据号码OrderID
                        FROM t_receivables
                        WHERE fID = '{}'
                '''
        super().__init__(Edit_ui(),
                         sql_main=m_sql,
                         PKValue=None,
                         edit_mode=JPEditFormDataMode.New,
                         flags=Qt.WindowFlags())
        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        JPPub().MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
        JPPub().MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')
        self.ui.butCancel.clicked.connect(self.close)
        self.ui.fID.hide()
        self.readData()
        self.ui.fPayeeID.refreshValueNotRaiseEvent(JPUser().currentUserID(), )
        self.__setEnabled()
        self.ui.fCustomerID.currentIndexChanged.connect(self.__setEnabled)
        self.ui.fCustomerID.setEditable(True)
        self.ui.fOrderID.setEditable(False)
        self.ui.fOrderID.setEnabled(False)
        self.ui.fArrears.setEnabled(True)
        self.ui.fCustomerID.setFocus()

    @property
    def _currentDate(self):
        return self.ui.fReceiptDate.date()

    @_currentDate.setter
    def _currentDate(self, d):
        self.ui.fReceiptDate.refreshValueNotRaiseEvent(d)

    def __setEnabled(self):
        self.ui.fCustomerID.setEnabled(True)
        self.ui.fCity.setEnabled(False)
        self.ui.fNUIT.setEnabled(False)
        self.ui.fEndereco.setEnabled(False)
        self.ui.fEndereco.setEnabled(False)
        self.ui.fCelular.setEnabled(False)
        self.ui.fTelefone.setEnabled(False)
        self.ui.fAmountPayable.setEnabled(False)
        self.ui.fAmountPaid.setEnabled(False)
        #self.ui.fArrears.setEnabled(False)
        self.ui.fPayeeID.setEnabled(False)

    def onGetFieldsRowSources(self):
        pub = JPPub()
        u_lst = [[item[1], item[0]] for item in JPUser().getAllUserList()]
        return [('fCustomerID', pub.getCustomerList(), 1),
                ('fPaymentMethodID', pub.getEnumList(3), 1),
                ('fPayeeID', u_lst, 1), ('fOrderID', [['DIBOTO']], 0)]

    def onGetPrintReport(self):
        return  #PrintOrder_report_Mob()

    def onDateChangeEvent(self, obj, value):
        nm = obj.objectName()
        if nm == 'fCustomerID':
            self.__customerIDChanged()

    def __customerIDChanged(self):
        # 刷新客户有关信息
        sql = '''
            SELECT fNUIT, fCity, fEndereco, fCelular, fContato
                , fTelefone, Q0.fAmountPayable  , Q1.fAmountPaid,
                Q0.fAmountPayable-Q1.fAmountPaid as fArrears,-1 as fPaymentMethodID
            FROM t_customer c
                LEFT JOIN (
                    SELECT fCustomerID, SUM(fPayable) AS fAmountPayable
                    FROM v_all_sales
                    WHERE fCustomerID = {CustomerID}
                ) Q0
                ON c.fCustomerID = Q0.fCustomerID
                LEFT JOIN (
                    SELECT fCustomerID, SUM(fAmountCollected) AS fAmountPaid
                    FROM t_receivables
                    WHERE fCustomerID = {CustomerID}
                ) Q1
                ON c.fCustomerID = Q1.fCustomerID
            WHERE c.fCustomerID = {CustomerID}
        '''
        sql = sql.format(CustomerID=self.ui.fCustomerID.Value())
        tab = JPQueryFieldInfo(sql)
        obj_name = [
            'fNUIT', 'fCity', 'fEndereco', 'fCelular', 'fContato', 'fTelefone',
            'fAmountPayable', 'fAmountPaid', 'fArrears'
        ]
        tup = (JPWidgets.QLineEdit, JPWidgets.QDateEdit, JPWidgets.QComboBox,
               JPWidgets.QTextEdit, JPWidgets.QCheckBox)
        fld_dict = tab.getRowFieldsInfoDict(0)
        for i, nm in enumerate(obj_name):
            obj = self.findChild(tup, nm)
            if obj:
                obj.setRowsData(tab.DataRows[0])
                obj.setMainModel(self)
                obj.setFieldInfo(fld_dict[nm])
                obj.refreshValueNotRaiseEvent(tab.getOnlyData([0, i]), True)

        # 刷新该客户名下当日单据号码
        sql_orderID = """
        select 'DIBOTO' as fOrderID
        union all 
        select 'Prepaid' as fOrderID
        union all 
        select fOrderID from t_order 
        where fCustomerID={CustomerID} 
            and fOrderDate=STR_TO_DATE('{dateString}', '%Y-%m-%d')
            and fConfirmed=1
            and fSubmited=1
            and fCanceled=0
        union all 
        select fOrderID from t_product_outbound_order 
        where fCustomerID={CustomerID} 
            and fOrderDate=STR_TO_DATE('{dateString}', '%Y-%m-%d')
            and fSubmited=1
            and fCanceled=0        
        """
        sql_orderID = sql_orderID.format(
            CustomerID=self.ui.fCustomerID.Value(),
            dateString=JPDateConver(self._currentDate, str))
        tab = JPQueryFieldInfo(sql_orderID)
        fld = self.ui.fOrderID.FieldInfo
        fld.RowSource = [[r.Datas[0]] for r in tab.DataRows]
        fld.BindingColumn = 0
        fld.Value = None
        fld.NotNull = True
        self.ui.fOrderID.setFieldInfo(fld, False)
        self.ui.fOrderID.setEnabled(True)

    def onAfterSaveData(self, data):
        JPPub().broadcastMessage(tablename="t_receivables", action='new', PK=data)
        self.ui.butSave.setEnabled(False)
        self.ListForm.dateChanged(data)
        self.ListForm.currentCustomerChanged()
