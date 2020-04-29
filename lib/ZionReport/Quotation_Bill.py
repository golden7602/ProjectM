from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter

from lib.JPDatabase.Database import JPDb
from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.JPPublc import JPPub
from lib.ZionReport.PrintingOrderReportMob import PrintOrder_report_Mob
from lib.JPFunction import JPGetDisplayText, JPDateConver
from lib.ZionReport.OrderReportMob import Order_report_Mob


class Quotation_Bill(Order_report_Mob):
    def __init__(self):
        super().__init__()
        self.CopyInfo = JPPub().getCopysInfo('BillCopys_QuotationOrder')
        self.Copys = len(self.CopyInfo)

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        if (SectionType == JPPrintSectionType.PageHeader and CurrentPage == 1):
            return True

    def init_ReportFooter(self):
        RF = self.ReportFooter
        RF.AddItemRect(1, (430, 0, 140, 20),
                       "金额合计SubTotal:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignRight)
        RF.AddItemRect(3, (570, 0, 80, 20),
                       "fAmount",
                       FormatString='{:,.2f}',
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 20, 140, 20),
                       "折扣Desconto:",
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(3, (570, 20, 80, 20),
                       "fDesconto",
                       AlignmentFlag=Qt.AlignRight,
                       FormatString='{:,.2f}',
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 40, 140, 20),
                       "税金IVA:",
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(3, (570, 40, 80, 20),
                       "fTax",
                       FormatString='{:,.2f}',
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 60, 140, 20),
                       "应付金额Valor a Pagar:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignRight)
        RF.AddItemRect(3, (570, 60, 80, 20),
                       "fPayable",
                       FormatString='{:,.2f}',
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(3, (0, 0, 430, 80),
                       "fNote1",
                       FormatString='备注Note:\n{}',
                       Bolder=True,
                       AlignmentFlag=(Qt.AlignLeft | Qt.TextWordWrap),
                       Font=self.font_YaHei_8)
        # 签字部分
        RF.AddItemRect(1, (0, 110, 100, 20),
                       '制作人 Productor:',
                       Bolder=False,
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (100, 125, 100, 0), '')

        RF.AddItemRect(1, (420, 110, 120, 20),
                       '审核人 Aprovar::',
                       Bolder=False,
                       AlignmentFlag=Qt.AlignRight,
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (540, 125, 100, 0), '')
        noteStr = JPPub().ConfigData()['Bank_Account'].split('\n')
        #noteStr = JPDb().getOnConfigValue('Bank_Account', str).split('\n')

        self.Arial_Black = QFont("Arial")
        self.Arial_Black.setPointSize(8)
        self.Arial_Black.setBold(True)

        for i, txt in enumerate(noteStr):
            RF.AddItem(1,
                       5,
                       135 + i * 15,
                       650,
                       20,
                       txt,
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignLeft | Qt.TextWordWrap),
                       Font=self.Arial_Black)
        # 下面的框要删除，因为跨页
        RF.AddItemRect(1, (0, 135, 650, len(noteStr) * 15), " ", Bolder=True)
        self.PageFooter.AddItemRect(4, (10, 0, 100, 20),
                                    '',
                                    FormatString='Page: {Page}/{Pages}',
                                    Bolder=False,
                                    AlignmentFlag=Qt.AlignLeft,
                                    Font=self.font_YaHei_8)
        self.PageFooter.AddItemRect(
            5, (110, 0, 540, 20),
            '',
            FormatString="PrintTime: %Y-%m-%d %H:%M:%S",
            Bolder=False,
            AlignmentFlag=Qt.AlignRight,
            Font=self.font_YaHei_8)

    def init_data(self, OrderID: str):
        SQL = """SELECT o.*
                    , if(isnull(fNote), ' ', fNote) AS fNote1
                    , d.fQuant, d.fProductName, d.fLength, d.fWidth, d.fPrice
                    , d.fAmount AS fAmountDetail
                FROM v_quotation o
                    RIGHT JOIN t_quotation_detail d ON o.fOrderID = d.fOrderID
                WHERE d.fOrderID = '{}'"""

        db = JPDb()
        data = db.getDict(SQL.format(OrderID))
        data.sort(key=lambda x: (x['fCustomerName'], x['fCity'], x['fAmount']
                                 is None, x['fAmount']))
        self.DataSource = data

    def PrintCurrentReport(self, OrderID: str):
        self.init_data(OrderID)
        self.init_ReportHeader_title(
            title1="报价单Cotação", title2="(ESTE DOCUMENTO É DO USO INTERNO)")
        self.init_ReportHeader()
        self.init_ReportHeader_Individualization()
        self.init_PageHeader()
        self.init_Detail()
        self.init_ReportFooter()
        # 大于6行自动更改纸型
        if len(self.DataSource) > 6:
            self.PaperSize = QPrinter.A4
            self.Orientation = QPrinter.Orientation(0)
        super().BeginPrint()
