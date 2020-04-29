from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter

from lib.JPDatabase.Database import JPDb
from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.JPPublc import JPPub
from lib.ZionReport.PrintingOrderReportMob import PrintOrder_report_Mob
from lib.JPFunction import JPGetDisplayText, JPDateConver


class FormReport_ProductInfo_InOutDetail(JPReport):
    def __init__(self,
                 PaperSize=QPrinter.A4,
                 Orientation=QPrinter.Orientation(0)):
        super().__init__(PaperSize, Orientation)
        self.configData = JPPub().getConfigData()
        self.font_YaHei = QFont("Microsoft YaHei")
        self.font_YaHei_8 = QFont(self.font_YaHei)
        self.font_YaHei_8.setPointSize(8)
        self.font_YaHei_12 = QFont(self.font_YaHei)
        self.font_YaHei_12.setPointSize(12)
        self.font_YaHei_10 = QFont(self.font_YaHei)
        self.font_YaHei_10.setPointSize(20)
        self.font_YaHei_10.setBold(True)
        self.BackColor = JPPub().getConfigData(
        )['PrintHighlightBackgroundColor']
        self.title_detail = [
            ' ', '产品名称ProductName', '入库In', '出库Out', '结余库存\nCurQua',
            '销售笔数\nBillCount'
        ]
        self.fns = [
            '序号ID', '产品名称ProductName', '入库数量In', '出库数量Out',
            '结余库存CurrentQuantity', '销售笔数BillCount'
        ]
        self.logo = JPPub().MainForm.logoPixmap
        self.title = 'Warehouse in/out Details\n出入库明细表'
        self.beginDate = None
        self.endDate = None

    def initItem(self):
        rpt = self
        rpt.PageHeader.AddItemRect(2, (0, 0, 274, 50), self.logo)
        rpt.PageHeader.AddItemRect(1, (274, 0, 376, 60),
                                   self.title,
                                   Bolder=False,
                                   AlignmentFlag=(Qt.AlignCenter),
                                   Font=self.font_YaHei_12)

        rpt.PageHeader.AddItemRect(1, (0, 50, 690, 20),
                                   'Date:{}'.format(
                                       JPDateConver(self.beginDate, str) +
                                       "--" + JPDateConver(self.endDate, str)),
                                   Bolder=False,
                                   AlignmentFlag=(Qt.AlignRight),
                                   Font=self.font_YaHei_8)

        cols = len(self.title_detail)
        al_c = Qt.AlignCenter
        al_r = (Qt.AlignVCenter | Qt.AlignRight)
        al_l = (Qt.AlignVCenter | Qt.AlignLeft)
        rpt.SetMargins(30, 30, 30, 30)
        title_height = 20
        rpt.ReportHeader.AddPrintLables(0,
                                        72,
                                        40,
                                        Texts=self.title_detail,
                                        Widths=[30, 420, 60, 60, 60, 60],
                                        Aligns=[al_c] * cols,
                                        AutoShrinkFont=True)
        rpt.Detail.addPrintRowCountItem(0,
                                        0,
                                        30,
                                        title_height,
                                        AlignmentFlag=al_c,
                                        Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (30, 0, 420, title_height),
                               '产品名称ProductName',
                               FormatString='{} ',
                               AlignmentFlag=al_l,
                               Font=self.font_YaHei_8)
        rpt.Detail.AddPrintFields(450,
                                  0,
                                  20,
                                  self.fns[2:], [60] * 4, [al_r] * 4,
                                  FormatString='{:,.0f}',
                                  Font=self.font_YaHei_8)

        # 页脚
        self.PageFooter.AddItemRect(4, (10, 0, 100, 20),
                                    '',
                                    FormatString='Page: {Page}/{Pages}',
                                    Bolder=False,
                                    AlignmentFlag=Qt.AlignLeft,
                                    Font=self.font_YaHei_8)
        self.PageFooter.AddItemRect(
            5, (0, 0, 650, 20),
            '',
            FormatString="PrintTime: %Y-%m-%d %H:%M:%S",
            Bolder=False,
            AlignmentFlag=Qt.AlignRight,
            Font=self.font_YaHei_8)
        self.DataSource = JPDb().getDict(self.sql)

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        return False
