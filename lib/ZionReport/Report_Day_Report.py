from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.ZionReport.PrintingOrderReportMob import PrintOrder_report_Mob
from PyQt5.QtCore import Qt
from lib.JPPublc import JPPub
from lib.JPDatabase.Database import JPDb
from PyQt5.QtGui import QFont
from lib.JPPrint.JPPrintReport import JPReport
from PyQt5.QtPrintSupport import QPrinter
from lib.JPFunction import JPGetDisplayText, JPDateConver


class FormReport_Day_print(JPReport):
    def __init__(self,
                 flds,
                 myyear,
                 baseon,
                 PaperSize=QPrinter.A3,
                 Orientation=QPrinter.Orientation(1)):
        super().__init__(PaperSize, Orientation)

        self.font_YaHei = QFont("微软雅黑")
        self.font_YaHei_8 = QFont(self.font_YaHei)
        self.font_YaHei_8.setPointSize(8)
        self.font_YaHei_10 = QFont(self.font_YaHei)
        self.font_YaHei_10.setPointSize(20)
        self.font_YaHei_10.setBold(True)
        rpt = self
        rpt.logo = JPPub().MainForm.logoPixmap
        rpt.ReportHeader.AddItemRect(2, (0, 0, 274, 50), rpt.logo)
        rpt.ReportHeader.AddItemRect(1, (274, 0, 110 * 13 - 274, 40),
                                     'Year Report 收款年报表',
                                     Bolder=False,
                                     AlignmentFlag=(Qt.AlignCenter),
                                     Font=self.font_YaHei_10)
        self.ReportHeader.AddItemRect(
            1, (274, 30, 110 * 13 - 274, 20),
            '基于Base on: {baseon}  年度Year: {myyear}'.format(baseon=baseon,
                                                           myyear=myyear),
            Bolder=False,
            AlignmentFlag=(Qt.AlignRight))

        title = [fld.Title for fld in flds]
        fns = [fld.FieldName for fld in flds]
        cols = len(flds)
        al_c = Qt.AlignCenter
        al_r = (Qt.AlignVCenter | Qt.AlignRight)
        rpt.SetMargins(30, 60, 30, 30)
        rpt.ReportHeader.AddPrintLables(0,
                                        60,
                                        50,
                                        Texts=title,
                                        Widths=[110] * cols,
                                        Aligns=[al_c] * cols)
        rpt.Detail.AddPrintFields(0,
                                  0,
                                  25,
                                  FieldNames=[fns[0]],
                                  Widths=[110],
                                  Aligns=[al_c])
        for i in range(1, cols):
            rpt.Detail.AddItemRect(3, (i * 110, 0, 110, 25),
                                   fns[i],
                                   Font=QFont('Times New Roman', 12),
                                   AlignmentFlag=al_r,
                                   FormatString='{:,.2f} ')
        self.PageFooter.AddItemRect(4, (10, 0, 110, 20),
                                    '',
                                    FormatString='Page: {Page}/{Pages}',
                                    Bolder=False,
                                    AlignmentFlag=(Qt.AlignLeft
                                                   | Qt.AlignVCenter),
                                    Font=self.font_YaHei_8)
        self.PageFooter.AddItemRect(
            5, (110 * 10, 0, 110 * 3, 20),
            '',
            FormatString="PrintTime: %Y-%m-%d %H:%M:%S",
            Bolder=False,
            AlignmentFlag=Qt.AlignRight,
            Font=self.font_YaHei_8)

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        return False
