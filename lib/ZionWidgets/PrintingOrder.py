from functools import reduce
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import pyqtSlot, Qt, QRect, QDate
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap, QKeyEvent, QColor
from PyQt5.QtWidgets import QAction, QLineEdit, QMessageBox

from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPMvc.JPEditFormModel import JPFormModelMain
from lib.JPMvc.JPFuncForm import JPFunctionForm, JPEditFormDataMode
from lib.JPPrint.JPPrintReport import JPPrintSectionType
from lib.JPPublc import JPPub, JPUser
from lib.ZionReport.PrintingOrderReportMob import PrintOrder_report_Mob
from lib.ZionWidgets.EditFormOrderOrPrintingOrder import JPFormPrintingOrder
from lib.JPFunction import JPRound
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.ZionWidgets.ViewPic import Form_ViewPic
from lib.JPPrint.JPPrintReport import JPReport
from PyQt5.QtPrintSupport import QPrinter


class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ok_icon = JPPub().MainForm.getIcon('yes.ico')

    def data(self, index, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        tab = self.TabelFieldInfo
        if c == 4:
            if role == Qt.DecorationRole:
                if tab.getOnlyData((r, c)):
                    return self.ok_icon
            else:
                return super().data(index, role=role)
        else:
            return super().data(index, role=role)


class JPFuncForm_PrintingOrder(JPFunctionForm):
    def __init__(self, MainForm):
        super().__init__(MainForm)
        sql_0 = """
                SELECT   fOrderID as `订单号码OrderID`, 
                    fCustomerName as `客户名Cliente`, 
                    fOrderDate as `日期OrderDate`, 
                    fRequiredDeliveryDate as `fRequiredDeliveryDate`, 
                    fSubmited1 as `提交Submited`, 
                    fSubmit_Name as `fSubmit_Name`, 
                    fEspecie as `类别Especie`, 
                    fAmount as `金额SubTotal`, 
                    fTax as `税金IVA`, 
                    fPayable as `应付金额Valor a Pagar`, 
                    fDesconto as `折扣Desconto`, 
                    fNumerBegin as `起始号码fNumerBegin`, 
                    fNumerEnd as `结束号码fNumerEnd`, 
                    fQuant as `数量fQuant`, 
                    fPagePerVolumn as `每本页数 Page/Vol`, 
                    fAvista as `每页序号Avista`, 
                    fTamanho as `尺寸Tamanho`, 
                    fVendedor as `联系人fVendedor`, 
                    fNrCopy as `联数Nr.Copy`, 
                    fContato as `联系人Contato`, 
                    fCelular as `手机Celular`, 
                    fTelefone as `fTelefone`, 
                    fEntry_Name as `录入Entry`, 
                    fCustomerID as `客户编号CustomerID`,  
                    cast(fSubmited as SIGNED) AS `fSubmited`
                FROM v_order AS o"""
        sql_1 = sql_0 + """
                WHERE fCanceled=0
                        AND left(fOrderID,2)='TP'
                        AND (fSubmited={ch1}
                        OR fSubmited={ch2})
                        AND fOrderDate{date}
                ORDER BY  fOrderID DESC"""
        sql_2 = sql_0 + """
                WHERE fCanceled=0
                        AND left(fOrderID,2)='TP'
                ORDER BY  fOrderID DESC"""
        self.backgroundWhenValueIsTrueFieldName = ['fSubmited']
        self.checkBox_1.setText('Submited')
        self.checkBox_2.setText('UnSubmited')
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(True)
        super().setListFormSQL(sql_1, sql_2)
        self.tableView.setColumnHidden(23, True)
        self.tableView.setColumnHidden(24, True)
        self.fSubmited_column = 24
        m_sql = """
                SELECT fOrderID
                , fCelular
                , fRequiredDeliveryDate
                , fContato
                , fVendedorID as 销售Vendedor
                , fCustomerID
                , fOrderDate
                , fTelefone
                , fQuant
                , fNumerBegin
                , fNumerEnd
                , fPrice
                , fLogo
                , fEspecieID
                , fAvistaID
                , fTamanhoID
                , fNrCopyID
                , fPagePerVolumn
                , fNote
                , fAmount
                , fDesconto
                , fTax
                , fPayable
                , fEntryID
                FROM t_order
                WHERE fOrderID = '{}'
                """
        self.setEditFormSQL(m_sql, None)
        self.pub = JPPub()
        self.pub.UserSaveData.connect(self.UserSaveData)

    def UserSaveData(self, tbName):
        if tbName == 't_order':
            self.refreshListForm()

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        frm = EditForm_PrintingOrder(sql_main=sql_main,
                                     edit_mode=edit_mode,
                                     sql_sub=sql_sub,
                                     PKValue=PKValue)
        if edit_mode != JPEditFormDataMode.ReadOnly:
            frm.ui.fCustomerID.setEditable(True)
        frm.ui.fOrderID.setEnabled(False)
        frm.ui.fCity.setEnabled(False)
        frm.ui.fNUIT.setEnabled(False)
        frm.ui.fEntryID.setEnabled(False)
        frm.ui.fEndereco.setEnabled(False)
        frm.ui.fEmail.setEnabled(False)
        return frm

    def onGetModelClass(self):
        return myJPTableViewModelReadOnly

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
        msg = '提交后订单将不能修改！确定继续提交记录【{cu_id}】吗？\n'
        msg = msg + 'The order "{cu_id}" will not be modified after submission. '
        msg = msg + 'Click OK to continue submitting?'
        msg = msg.replace("{cu_id}", str(cu_id))
        reply = QMessageBox.question(self, '确认', msg,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            sql = "update {tn} set fSubmited=1 where {pk_n}='{pk_v}';"
            sql1 = "select '{pk_v}';"
            sql = sql.format(tn=self.EditFormMainTableName,
                             pk_n=self.EditFormPrimarykeyFieldName,
                             pk_v=cu_id)
            db.executeTransaction([sql, sql1.format(pk_v=cu_id)])
            JPPub().broadcastMessage(tablename="t_order",
                                     PK=cu_id,
                                     action='Submit')
            self.refreshListForm()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.model.TabelFieldInfo,
                                           self.MainForm)
        exp.run()

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


class myHistoryView(JPTableViewModelReadOnly):
    def __init__(self, tableView, tabelFieldInfo):
        super().__init__(tableView, tabelFieldInfo)

    def data(self, Index, role):

        if role == Qt.BackgroundColorRole:
            if Index.row() == 0 and Index.column() == 4:
                return QColor(Qt.blue)
            else:
                return super().data(Index, role)
        if role == Qt.TextColorRole:
            if Index.row() == 0 and Index.column() == 4:
                return QColor(Qt.white)
            else:
                return super().data(Index, role)
        return super().data(Index, role)


class EditForm_PrintingOrder(JPFormModelMain):
    def __init__(self, sql_main, sql_sub=None, edit_mode=None, PKValue=None):
        super().__init__(JPFormPrintingOrder(),
                         sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode)
        JPPub().MainForm.addLogoToLabel(self.ui.label_logo)
        self.ui.butTaxCer.setIcon(JPPub().MainForm.getIcon('rosette.ico'))
        self.setPkRole(5)
        self.cacuTax = True
        self.NumberControl = False
        self.ui.fTax.keyPressEvent = self.__onTaxKeyPress
        self.readData()
        self.ui.fNumerBegin.setEnabled(False)
        self.ui.fNumerEnd.setEnabled(False)
        if self.isNewMode:
            self.ui.butTaxCer.setEnabled(False)
            uid = JPUser().currentUserID()
            self.ui.fEntryID.refreshValueNotRaiseEvent(uid)
            self.ui.fOrderDate.refreshValueNotRaiseEvent(QDate.currentDate())
        # 编辑状态下，更新一次历史单据号列表
        if self.isEditMode or self.isReadOnlyMode:
            self.onDateChangeEvent(self.ui.fCustomerID, None)
        # 设置必输入字段
        self.ui.fCustomerID.FieldInfo.NotNull = True
        self.ui.fEspecieID.FieldInfo.NotNull = True
        self.ui.fAvistaID.FieldInfo.NotNull = True
        self.ui.fQuant.FieldInfo.NotNull = True
        self.ui.fPagePerVolumn.FieldInfo.NotNull = True
        self.ui.fTamanhoID.FieldInfo.NotNull = True
        self.ui.fPrice.FieldInfo.NotNull = True
        self.ui.fRequiredDeliveryDate.FieldInfo.NotNull = True
        self.ui.fVendedorID.FieldInfo.NotNull = True
        self.ui.fNrCopyID.FieldInfo.NotNull = True
        self.ui.fCustomerID.setFocus()
        self.ui.fQuant.setIntValidator(-9999999999, 9999999999)

    def __onTaxKeyPress(self, KeyEvent: QKeyEvent):
        if (KeyEvent.modifiers() == Qt.AltModifier
                and KeyEvent.key() == Qt.Key_Delete):
            self.ui.fTax.refreshValueRaiseEvent(None, True)
            self.cacuTax = False
        elif (KeyEvent.modifiers() == Qt.AltModifier
              and KeyEvent.key() == Qt.Key_T):
            self.cacuTax = True

    def onGetFieldsRowSources(self):
        pub = JPPub()
        u_lst = [[item[1], item[0]] for item in JPUser().getAllUserList()]
        return [('fCustomerID', pub.getCustomerList(), 1),
                ('fVendedorID', pub.getEnumList(10), 1),
                ('fEspecieID', pub.getEnumList(2), 1),
                ('fAvistaID', pub.getEnumList(7), 1),
                ('fTamanhoID', pub.getEnumList(8), 1),
                ('fNrCopyID', pub.getEnumList(9), 1), ('fEntryID', u_lst, 1)]

    def onGetPrintReport(self):
        return PrintOrder_report_Mob()

    def onGetReadOnlyFields(self):
        return [
            'fOrderID', "fNumerEnd", "fEntryID", 'fAmount', 'fPayable', 'fNUIT'
        ]

    @property
    def sql_base(self):
        return '''
            SELECT fOrderID AS 单据号码OrderID,
                fOrderDate as 单据日期OrderDate,
                CAST(e.fTitle AS char(20)) AS 类别Especie,
                CAST(fNumerBegin AS SIGNED) AS 起始号码NumerBegin,
                CAST(fNumerEnd AS SIGNED) AS 结束号码NumerEnd
            FROM t_order o
                LEFT JOIN t_enumeration e ON o.fEspecieID = e.fItemID
            '''

    def onAfterSaveData(self, data):
        act = 'new' if self.isNewMode else 'edit'
        JPPub().broadcastMessage(tablename="t_order", PK=data, action=act)
        if self.isNewMode:
            self.ui.fOrderID.refreshValueNotRaiseEvent(data, True)

    def setNumberNeedControl(self, arg=None):
        obj_begin = self.ui.fNumerBegin
        obj_end = self.ui.fNumerEnd
        self.NumberControl = True if arg else False
        if not arg:
            obj_begin.refreshValueNotRaiseEvent(None, True)
            obj_end.refreshValueNotRaiseEvent(None, True)
            sql = self.sql_base + JPDb().getOnlyStrcFilter()
            tab = JPQueryFieldInfo(sql)
            mod = myHistoryView(self.ui.listPrintingOrder, tab)
            self.ui.listPrintingOrder.setModel(mod)
            self.ui.listPrintingOrder.resizeColumnsToContents()
            obj_begin.setEnabled(False)
            self.ui.listPrintingOrder.setEnabled(False)
        else:
            tab = JPQueryFieldInfo(arg)
            mod = myHistoryView(self.ui.listPrintingOrder, tab)
            self.ui.listPrintingOrder.setModel(mod)
            self.ui.listPrintingOrder.resizeColumnsToContents()
            self.ui.listPrintingOrder.setEnabled(
                len(tab) > 0 and self.isEditMode)

            beginNum = tab.getOnlyData([0, 4]) if len(tab.DataRows) > 0 else 0
            beginNum += 1

            # 编辑状态时，不更新起始值，只修改编辑状态
            # 编辑和新增加状态时，设定起始、结束值的验证器
            if self.EditMode == JPEditFormDataMode.New:
                obj_begin.refreshValueNotRaiseEvent(beginNum, True)
            obj_begin.setIntValidator(beginNum, 999999999999)
            obj_begin.setEnabled(True)

    def tryNumberControl(self, obj):
        obj_cus = self.ui.fCustomerID
        obj_esp = self.ui.fEspecieID

        nm = obj.objectName()
        if nm == 'fCustomerID':
            c_id = self.ui.fCustomerID.Value()
            sql = f'''select fNUIT,fCity,fContato,fAreaCode,
                    fCelular,fTelefone,fEndereco,fEmail,
                    fWeb,fFax,fNote,fTaxRegCer
                    from t_customer 
                    where fCustomerID={c_id}'''
            dic = JPDb().getDict(sql)[0]
            self.ui.fCelular.refreshValueNotRaiseEvent(dic['fCelular'], True)
            self.ui.fContato.refreshValueNotRaiseEvent(dic['fContato'], True)
            self.ui.fTelefone.refreshValueNotRaiseEvent(dic['fTelefone'], True)
            self.ui.fNUIT.setText(dic['fNUIT'])
            self.ui.fCity.setText(dic['fCity'])
            self.ui.fEndereco.setText(dic['fEndereco'])
            self.ui.fEmail.setText(dic['fEmail'])
            ID = dic['fTaxRegCer']
            ZT = True if ID else False
            self.ui.butTaxCer.setEnabled(ZT)
            self.ui.butTaxCer.ID = ID
        # 判断是否需要单据管理,不需要管理则退出
        if obj_cus.currentIndex() == -1 or obj_esp.currentIndex() == -1:
            self.setNumberNeedControl(False)
            return
        else:
            if obj_esp.currentData()[2] != '1':
                self.setNumberNeedControl(False)
                return

        # 需要管理情况下：
        # 新增状态
        # 检查数据库中是否存在同客户同类型未确认的单据
        # 如果有，则清除当前控件的输入，提示信息并退出
        db = JPDb()
        orderSQL = " ORDER BY fNumerEnd DESC"
        if self.isNewMode:
            where = """ 
            WHERE fCustomerID={uid} 
                and fEspecieID={tid}
                and fConfirmed={zt}
                and fCanceled=0
            """
            sql = 'select fOrderID from t_order'
            sql = sql + where.format(
                uid=obj_cus.Value(), tid=obj_esp.Value(), zt=0)
            bc, result = db.executeTransaction(sql)
            if result:
                txt = '选择的客户名(相同分公司类型)下有同类型但未确认的单据，不能增加新单据!\n'
                txt = txt + 'There are identical but uncertain documents '
                txt = txt + 'under the name of the selected customer, '
                txt = txt + 'and no new documents can be added'
                QMessageBox.information(self, "提示", txt)
                return
            else:

                num_sql = self.sql_base + where.format(
                    uid=obj_cus.Value(), tid=obj_esp.Value(), zt=1)
                self.setNumberNeedControl(num_sql + orderSQL)
            return

        # 需要管理情况下：
        # 编辑状态
        if self.isEditMode or self.isReadOnlyMode:
            where = """ WHERE fCustomerID={uid} and fEspecieID={tid} and fConfirmed={zt}
                    and fOrderID<'{id}'"""
            where = where.format(uid=obj_cus.Value(),
                                 tid=obj_esp.Value(),
                                 zt=1,
                                 id=self.ui.fOrderID.Value())
            num_sql = self.sql_base + where
            self.setNumberNeedControl(num_sql + orderSQL)

    def cacu_amount(self, obj):
        nm = obj.objectName()
        fQuant = self.ui.fQuant.Value()
        fPrice = self.ui.fPrice.Value()
        temp_fDesconto = self.ui.fDesconto.Value()
        fDesconto = temp_fDesconto if temp_fDesconto else 0
        fAmount = (fQuant * fPrice if all((fQuant, fPrice)) else None)
        self.ui.fAmount.refreshValueNotRaiseEvent(fAmount, True)
        if fAmount is None:
            self.ui.fTax.refreshValueNotRaiseEvent(None, True)
            self.ui.fPayable.refreshValueNotRaiseEvent(None, True)
            return
        if nm == "fTax":
            temp_fTax = self.ui.fTax.Value()
            fTax = temp_fTax if temp_fTax else 0
        else:
            fTax = JPRound((fAmount - fDesconto) * 0.17) if fAmount else 0
        if self.cacuTax:
            self.ui.fTax.refreshValueNotRaiseEvent(fTax, True)
        else:
            fTax = 0
        fPayable = fAmount + fTax - fDesconto
        self.ui.fPayable.refreshValueNotRaiseEvent(fPayable, True)

    def tryRefreshNumber(self):
        if self.NumberControl:
            temp_fAvistaID = self.ui.fAvistaID.currentData()
            fNumerBegin = self.ui.fNumerBegin.Value()
            fAvistaID = int(temp_fAvistaID[2]) if temp_fAvistaID else None
            fQuant = self.ui.fQuant.Value()
            fPagePerVolumn = self.ui.fPagePerVolumn.Value()
            if all((fAvistaID, fQuant, fPagePerVolumn)):
                fNumerEnd = fNumerBegin + fAvistaID * fQuant * fPagePerVolumn - 1
            else:
                fNumerEnd = fNumerBegin
            self.ui.fNumerEnd.refreshValueNotRaiseEvent(fNumerEnd, True)

    def onDateChangeEvent(self, obj, value):
        nm = obj.objectName()
        if nm in ('fCustomerID', 'fEspecieID'):
            self.tryNumberControl(obj)
        if nm in ('fQuant', 'fPrice', 'fDesconto', "fTax"):
            self.cacu_amount(obj)
        elif nm in ('fNumerBegin', 'fAvistaID', 'fQuant', 'fPagePerVolumn'):
            self.tryRefreshNumber()

    @pyqtSlot()
    def on_butPrint_clicked(self):
        rpt = Order_Printingreport()
        rpt.PrintCurrentReport(self.ui.fOrderID.Value())

        ID = self.ui.butTaxCer.ID
        if ID:
            msg = '当前客户存在税务登记证，是否需要打印?\n'
            msg = msg + 'Current customers have tax '
            msg = msg + 'registration certificates, do you need to print them?'
            reply = QMessageBox.question(self, '确认', msg,
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                pixmap = JPPub().MainForm.getTaxCerPixmap(ID)
                rpt1 = printTaxCer()
                rpt1.PrintCurrentReport(pixmap)

    @pyqtSlot()
    def on_butTaxCer_clicked(self):
        fn = self.ui.butTaxCer.ID
        Form_ViewPic(self, JPPub().MainForm.getTaxCerPixmap(fn))


class Order_Printingreport(PrintOrder_report_Mob):
    def __init__(self):
        super().__init__()

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        if (SectionType == JPPrintSectionType.PageHeader and CurrentPage == 1):
            return True

    def PrintCurrentReport(self, OrderID: str):
        self.init_data(OrderID)
        self.init_ReportHeader_title(
            title1="NOTA DE PAGAMENTO",
            title2="(ESTE DOCUMENTO É DO USO INTERNO)")
        self.init_ReportHeader()
        self.init_PageHeader()
        self.init_ReportFooter()
        super().BeginPrint()


class printTaxCer(JPReport):
    def __init__(self,
                 PaperSize=QPrinter.A4,
                 Orientation=QPrinter.Orientation(0)):
        super().__init__(PaperSize, Orientation)

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        if (SectionType == JPPrintSectionType.PageHeader and CurrentPage == 1):
            return True

    def PrintCurrentReport(self, pixmap: str):
        p = QPrinter()
        p.setPaperSize(QPrinter.A4)
        p.setOrientation(QPrinter.Orientation(0))
        self.SetMargins(0, 0, 0, 0)
        rect = p.pageRect()
        self.ReportHeader.AddItem(2, 0, 0, rect.width(), rect.height(), pixmap)
        super().BeginPrint()
