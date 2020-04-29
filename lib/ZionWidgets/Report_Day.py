from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import Qt, QDate, pyqtSlot, QVariant  #, QMetaObject, pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QAbstractItemView
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from Ui.Ui_FormReport_Day import Ui_Form
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPFunction import findButtonAndSetIcon
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from lib.JPPublc import JPPub
from lib.ZionReport.Report_Day_Report import FormReport_Day_print


class _myMod(JPTableViewModelReadOnly):
    def __init__(self, *args):
        super().__init__(*args)
        self.f = QFont()
        self.f.Black = True
        self.f.setBold(True)

    # def headerData(self, section, Orientation,
    #                role: int = Qt.DisplayRole) -> QVariant():

    #     if role == Qt.DisplayRole:
    #         if Orientation == Qt.Horizontal:
    #             return QVariant(self.titles[section - 1])
    #     return super().headerData(section, Orientation, role)

    def data(self, Index, role: int = Qt.DisplayRole):
        r, c = Index.row(), Index.column()
        clr = QColor(245, 245, 245)
        if c == 0 and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if c == 0 and role == Qt.BackgroundColorRole:
            return clr
        if c == 0 and role == Qt.FontRole:
            return self.f
        if r == (super().rowCount() - 1) and role == Qt.BackgroundColorRole:
            return clr
        if r == (super().rowCount() - 1) and role == Qt.FontRole:
            return self.f
        # if c == 0 and role == Qt.DisplayRole:
        #     cn = self.TabelFieldInfo.DataRows[r].Datas[c]
        #     if cn == 'Sum':
        #         return QVariant(cn)
        #     else:
        #         return QVariant(self.days[int(cn) - 1])
        return super().data(Index, role)


class Form_Repoet_Day(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        mainform.addOneButtonIcon(self.ui.CmdPrint, 'print.png')
        mainform.addOneButtonIcon(self.ui.CmdPDF, 'pdf.png')
        mainform.addOneButtonIcon(self.ui.CmdExportToExcel, 'exportToexcel.png')
        year_sql = """
                select year(fOrderDate) as y  
                from t_order union select year(fReceiptDate) 
                as y from t_receivables
        """
        self.sql_none = """
            SELECT Null AS `Day\Month`,
            Null as M1, Null as M2, Null as M3, Null as M4, 
            Null as M5, Null as M6, Null as M7, Null as M8, 
            Null as M9, Null as M10, Null as M11, Null as M12 
            from  t_order {}
        """
        sql_receivables = """
            SELECT IF(ISNULL(Q3.d), 'Sum', Q3.d) AS `Day\Month`
                , M1, M2, M3, M4, M5, M6, M7, M8, M9, M10
                , M11, M12
            FROM (
                SELECT Q1.d
                    , sum(IF(Q1.m = 1, Q1.j1, NULL)) AS M1
                    , sum(IF(Q1.m = 2, Q1.j1, NULL)) AS M2
                    , sum(IF(Q1.m = 3, Q1.j1, NULL)) AS M3
                    , sum(IF(Q1.m = 4, Q1.j1, NULL)) AS M4
                    , sum(IF(Q1.m = 5, Q1.j1, NULL)) AS M5
                    , sum(IF(Q1.m = 6, Q1.j1, NULL)) AS M6
                    , sum(IF(Q1.m = 7, Q1.j1, NULL)) AS M7
                    , sum(IF(Q1.m = 8, Q1.j1, NULL)) AS M8
                    , sum(IF(Q1.m = 9, Q1.j1, NULL)) AS M9
                    , sum(IF(Q1.m = 10, Q1.j1, NULL)) AS M10
                    , sum(IF(Q1.m = 11, Q1.j1, NULL)) AS M11
                    , sum(IF(Q1.m = 12, Q1.j1, NULL)) AS M12
                FROM (
                    SELECT MONTH(fReceiptDate) AS m, DAY(fReceiptDate) AS d
                        , SUM(fAmountCollected) AS j1
                    FROM t_receivables
                    WHERE YEAR(fReceiptDate) = {}
                    GROUP BY MONTH(fReceiptDate), DAY(fReceiptDate)
                ) Q1
                GROUP BY Q1.d WITH ROLLUP
            ) Q3
        """
        sql_payment = """
                SELECT if(isnull(Q3.d), 'Sum', Q3.d) AS `Day\Month`
                    , M1, M2, M3, M4, M5, M6, M7, M8, M9, M10
                    , M11, M12
                FROM (
                    SELECT Q1.d
                        , sum(IF(Q1.m = 1, Q1.j1, NULL)) AS M1
                        , sum(IF(Q1.m = 2, Q1.j1, NULL)) AS M2
                        , sum(IF(Q1.m = 3, Q1.j1, NULL)) AS M3
                        , sum(IF(Q1.m = 4, Q1.j1, NULL)) AS M4
                        , sum(IF(Q1.m = 5, Q1.j1, NULL)) AS M5
                        , sum(IF(Q1.m = 6, Q1.j1, NULL)) AS M6
                        , sum(IF(Q1.m = 7, Q1.j1, NULL)) AS M7
                        , sum(IF(Q1.m = 8, Q1.j1, NULL)) AS M8
                        , sum(IF(Q1.m = 9, Q1.j1, NULL)) AS M9
                        , sum(IF(Q1.m = 10, Q1.j1, NULL)) AS M10
                        , sum(IF(Q1.m = 11, Q1.j1, NULL)) AS M11
                        , sum(IF(Q1.m = 12, Q1.j1, NULL)) AS M12
                    FROM (
                        SELECT MONTH(fOrderDate) AS m, DAY(fOrderDate) AS d
                            , SUM(fPayable) AS j1
                        FROM t_order
                        WHERE (Year(fOrderDate) = {}
                            AND fCanceled = 0
                            AND fSubmited = 1
                            AND fConfirmed = 1)
                        GROUP BY MONTH(fOrderDate), DAY(fOrderDate)
                    ) Q1
                    GROUP BY Q1.d WITH ROLLUP
                ) Q3        """
        self.cbo_base = self.ui.cbo_base
        self.cbo_year = self.ui.cbo_year
        self.tableView = self.ui.tableView
        self.cbo_base.addItem('Payment', sql_payment)
        self.cbo_base.addItem('Receivables', sql_receivables)
        db = JPDb()
        year_list = db.getDataList(year_sql)
        year_list = [str(y[0]) for y in year_list if y[0]]
        for y in year_list:
            self.cbo_year.addItem(y)
        cur_year = str(QDate.currentDate().year())
        if  cur_year in year_list:
            self.cbo_year.setCurrentText(cur_year)
        else:
            self.cbo_year.setCurrentIndex(-1)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cbo_base.currentTextChanged.connect(self._search)
        self.cbo_year.currentTextChanged.connect(self._search)
        #self.butPrint.clicked.connect(self.onbutPrint)
        self._search()

    def __changeTitle(self, tab: JPQueryFieldInfo):
        titles = [
            '一月Jan', '二月Feb', '三月Mar', '四月Apr', '五月May', '六月June', '七月July',
            '八月Aug', '九月Sept', '十月Oct', '十一月Nov', '十二月Dec'
        ]
        days = [
            '1(st)', '2(nd)', '3(rd)', '4(th)', '5(th)', '6(th)', '7(th)',
            '8(th)', '9(th)', '10(th)', '11(th)', '12(th)', '13(th)', '14(th)',
            '15(th)', '16(th)', '17(th)', '18(th)', '19(th)', '20(th)',
            '21(st)', '22(nd)', '23(rd)', '24(th)', '25(th)', '26(th)',
            '27(th)', '28(th)', '29(th)', '30(th)', '31(st)'
        ]
        for i, fld in enumerate(tab.Fields):
            if i > 0:
                fld.FieldName = titles[i - 1]
                fld.Title = titles[i - 1]
        l_tab = len(tab)
        for i, r in enumerate(tab.DataRows):
            if i != l_tab - 1:
                r.Datas[0] = days[int(r.Datas[0])-1]

    def _search(self):
        db = JPDb()
        sql = self.cbo_base.currentData() if (
            self.cbo_base.currentIndex() != -1
            and self.cbo_year.currentIndex() != -1) else self.sql_none.format(
                db.getOnlyStrcFilter())
        tab = JPQueryFieldInfo(sql.format(self.cbo_year.currentText()))
        self.__changeTitle(tab)
        self.queryInfo = tab
        self.mod = _myMod(self.tableView, self.queryInfo)
        self.tableView.setModel(self.mod)

    @pyqtSlot()
    def on_CmdPrint_clicked(self):
        if len(self.queryInfo) == 0:
            return
        flds = self.queryInfo.Fields
        rpt = FormReport_Day_print(flds, self.cbo_year.currentText(),
                                   self.cbo_base.currentText())
        rpt.DataSource = self.mod.getDataDict(Qt.EditRole)
        rpt.BeginPrint()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        exp = JPExpExcelFromTabelFieldInfo(self.mod.TabelFieldInfo,
                                           self.MainForm)
        exp.run()

