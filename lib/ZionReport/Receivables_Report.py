from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from lib.ZionReport.PrintingOrderReportMob import PrintOrder_report_Mob
from PyQt5.QtCore import Qt
from lib.JPPublc import JPPub
from lib.JPDatabase.Database import JPDb
from PyQt5.QtGui import QFont, QColor
from lib.JPPrint.JPPrintReport import JPReport
from PyQt5.QtPrintSupport import QPrinter
from lib.JPFunction import JPGetDisplayText, JPDateConver
from lib.JPDatabase.Query import JPQueryFieldInfo


class FormReport_Rec_print(JPReport):
    def __init__(self,
                 curdate,
                 cur_tab,
                 tongji_tab,
                 dateString,
                 PaperSize=QPrinter.A4,
                 Orientation=QPrinter.Orientation(0)):
        super().__init__(PaperSize, Orientation)
        self.configData = JPPub().getConfigData()
        self.font_YaHei = QFont("Microsoft YaHei")
        self.font_YaHei_8 = QFont(self.font_YaHei)
        self.font_YaHei_8.setPointSize(8)
        self.font_YaHei_10 = QFont(self.font_YaHei)
        self.font_YaHei_10.setPointSize(20)
        self.font_YaHei_10.setBold(True)
        self.BackColor = JPPub().getConfigData(
        )['PrintHighlightBackgroundColor']
        rpt = self

        rpt.logo = JPPub().MainForm.logoPixmap
        rpt.ReportHeader.AddItemRect(2, (0, 0, 274, 50), rpt.logo)
        rpt.ReportHeader.AddItemRect(1, (274, 0, 446, 60),
                                     'de vendas diárias 收款日报表',
                                     Bolder=False,
                                     AlignmentFlag=(Qt.AlignCenter),
                                     Font=self.font_YaHei_10)

        rpt.ReportHeader.AddItemRect(1, (0, 50, 720, 20),
                                     'Date:{}'.format(curdate),
                                     Bolder=False,
                                     AlignmentFlag=(Qt.AlignRight),
                                     Font=self.font_YaHei_8)

        title = [
            '序号\nID', '客户名\nCliente', '收款额\nAmount', '收款人\nfPayee',
            '收款方式\nModoPago', '单据号\nOrderID', '备注\nNote'
        ]

        fns = [
            'fID', 'fCustomerName', 'fAmountCollected', 'fPayee',
            'fPaymentMethod', 'fOrderID', 'fNote'
        ]
        cols = 7
        al_c = Qt.AlignCenter
        al_r = (Qt.AlignVCenter | Qt.AlignRight)
        al_l = (Qt.AlignVCenter | Qt.AlignLeft)
        rpt.SetMargins(30, 30, 30, 30)
        rpt.ReportHeader.AddPrintLables(0,
                                        72,
                                        40,
                                        Texts=title,
                                        Widths=[40, 210, 80, 80, 100, 120, 90],
                                        Aligns=[al_c] * cols)
        rpt.Detail.addPrintRowCountItem(0,
                                        0,
                                        40,
                                        20,
                                        AlignmentFlag=al_c,
                                        Font=self.font_YaHei_8)
        rpt.Detail.AddItem(
            3,
            40,
            0,
            210,
            20,
            fns[1],
            FormatString=' {}',
            AlignmentFlag=al_l,
            # 超出长度省略
            AutoShrinkFont=self.configData['AutoShrinkFonts'],
            AutoEllipsis=self.configData['AutoEllipsis'],
            Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (250, 0, 80, 20),
                               fns[2],
                               AlignmentFlag=al_r,
                               FormatString='{:,.2f} ',
                               Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (330, 0, 80, 20),
                               fns[3],
                               AlignmentFlag=al_c,
                               Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (410, 0, 100, 20),
                               fns[4],
                               AlignmentFlag=al_c,
                               Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (510, 0, 120, 20),
                               fns[5],
                               AlignmentFlag=al_l,
                               FormatString=' {}',
                               Font=self.font_YaHei_8)
        rpt.Detail.AddItemRect(3, (630, 0, 90, 20),
                               fns[6],
                               AlignmentFlag=al_l,
                               FormatString=' {}',
                               Font=self.font_YaHei_8)

        sum_j = 0
        for i in range(len(cur_tab)):
            sum_j += cur_tab.getOnlyData([i, 4])

        rpt.ReportFooter.AddPrintLables(
            0,
            0,
            20,
            Texts=["合计Sum", JPGetDisplayText(sum_j), " "],
            Widths=[250, 80, 390],
            Aligns=[al_c, al_r, al_c],
            FillColor=self.BackColor,
            Font=self.font_YaHei_8)

        sql_payable = f"""
            SELECT SUM(fPayable) AS sumPayable, 
                COUNT(fOrderID) AS countOrderID
            FROM v_all_sales
            WHERE (fOrderDate = STR_TO_DATE('{dateString}', '%Y-%m-%d'))
        """
        sql_SKFS = f"""
        select if(isnull(Q.fPaymentMethod),'Sum合计',Q.fPaymentMethod) as skfs,
            Q.今日收款,Q.今日收款笔数,Q.DIBOTO,Q.DIBOTO笔数,Q.Prepaid,Q.Prepaid笔数,Q.小计Subtotal,Q.笔数小计Subcount
            from (
            SELECT fPaymentMethod
                , SUM(if(fOrderID = 'DIBOTO' or fOrderID = 'Prepaid', NULL, fAmountCollected)) AS 今日收款
                , COUNT(if(fOrderID = 'DIBOTO' or fOrderID = 'Prepaid', NULL, fAmountCollected)) AS 今日收款笔数
                , SUM(if(fOrderID = 'DIBOTO', fAmountCollected, NULL)) AS DIBOTO
                , COUNT(if(fOrderID = 'DIBOTO', fAmountCollected, NULL)) AS DIBOTO笔数
                , SUM(if(fOrderID = 'Prepaid', fAmountCollected, NULL)) AS Prepaid
                , COUNT(if(fOrderID = 'Prepaid', fAmountCollected, NULL)) AS Prepaid笔数
                , SUM(fAmountCollected) AS 小计Subtotal, COUNT(fAmountCollected) AS 笔数小计Subcount
            FROM v_receivables
            WHERE fReceiptDate=STR_TO_DATE('{dateString}', '%Y-%m-%d')
            GROUP BY fPaymentMethod WITH ROLLUP) as Q        
        """
        title_height = 20
        rpt.ReportFooter.AddItem(1,
                                 0,
                                 title_height,
                                 720,
                                 30,
                                 "本日结算方式统计Today's settlement statistics",
                                 Bolder=False,
                                 AlignmentFlag=al_c)
        title_height += 30
        title = ['方式PM', "收当日订单Today's Order Rec", '收欠款DIBOTO','预付款Prepaid', '小计SubTotle']
        rpt.ReportFooter.AddPrintLables(0,
                                        title_height,
                                        25,
                                        title,
                                        Widths=[120, 150, 150, 150, 150],
                                        Aligns=[al_c] * 5,
                                        Font=self.font_YaHei_8)
        tongji_tab = JPQueryFieldInfo(sql_SKFS)
        title_height += 25
        for r in range(len(tongji_tab)):
            FillColor = QColor(255, 255,
                               255) if r < (len(tongji_tab) - 1) else QColor(
                                   194, 194, 194)
            rpt.ReportFooter.AddItem(1,
                                     0,
                                     title_height + r * 20,
                                     120,
                                     20,
                                     tongji_tab.getDispText([r, 0]),
                                     FormatString=' {}',
                                     AlignmentFlag=al_l,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     120,
                                     title_height + r * 20,
                                     100,
                                     20,
                                     tongji_tab.getDispText([r, 1]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     220,
                                     title_height + r * 20,
                                     50,
                                     20,
                                     tongji_tab.getDispText([r, 2]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     270,
                                     title_height + r * 20,
                                     100,
                                     20,
                                     tongji_tab.getDispText([r, 3]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     370,
                                     title_height + r * 20,
                                     50,
                                     20,
                                     tongji_tab.getDispText([r, 4]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     420,
                                     title_height + r * 20,
                                     100,
                                     20,
                                     tongji_tab.getDispText([r, 5]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     520,
                                     title_height + r * 20,
                                     50,
                                     20,
                                     tongji_tab.getDispText([r, 6]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     570,
                                     title_height + r * 20,
                                     100,
                                     20,
                                     tongji_tab.getDispText([r, 7]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)
            rpt.ReportFooter.AddItem(1,
                                     670,
                                     title_height + r * 20,
                                     50,
                                     20,
                                     tongji_tab.getDispText([r, 8]),
                                     FormatString='{} ',
                                     AlignmentFlag=al_r,
                                     Font=self.font_YaHei_8,
                                     FillColor=self.BackColor)

        # 总结部分
        title_height += (len(tongji_tab) - 1) * 20
        title_height += 40
        title = [
            "当日订单应付Today's Order Payable",
            "收当日订单Today's Order Rec",
            '欠款Arrears',
        ]
        rpt.ReportFooter.AddPrintLables(120,
                                        title_height,
                                        25,
                                        title,
                                        Widths=[200, 200, 200],
                                        Aligns=[al_c] * 3,
                                        Font=self.font_YaHei_8)
        rpt.ReportFooter.AddItem(1,
                                 0,
                                 title_height,
                                 120,
                                 45,
                                 '总结\nsummary',
                                 FormatString='{} ',
                                 AlignmentFlag=al_c,
                                 Font=self.font_YaHei_8,
                                 FillColor=self.BackColor)

        title_height += 25
        payable_tab = JPQueryFieldInfo(sql_payable)
        v1 = payable_tab.getOnlyData([0, 0])
        v2 = tongji_tab.getOnlyData([len(tongji_tab) - 1, 1])
        v3 = '{:,.2f}'.format((v1 if v1 else 0) - (v2 if v2 else 0))
        ShouDangRiDingDan = tongji_tab.getDispText([len(tongji_tab) - 1, 1
                                                    ]) + " " if v2 else "0 "
        txt = [
            payable_tab.getDispText([0, 0]) + " ",
            JPGetDisplayText(len(payable_tab), str) + " ", ShouDangRiDingDan,
            tongji_tab.getDispText([len(tongji_tab)-1,2]) +
            " ", v3 + " "
        ]
        rpt.ReportFooter.AddPrintLables(120,
                                        title_height,
                                        20,
                                        txt,
                                        Widths=[150, 50, 150, 50, 200],
                                        Aligns=[al_r] * 5,
                                        Font=self.font_YaHei_8,
                                        FillColor=self.BackColor)

        # 页脚
        self.PageFooter.AddItemRect(4, (10, 0, 100, 20),
                                    '',
                                    FormatString='Page: {Page}/{Pages}',
                                    Bolder=False,
                                    AlignmentFlag=Qt.AlignLeft,
                                    Font=self.font_YaHei_8)
        self.PageFooter.AddItemRect(
            5, (0, 0, 720, 20),
            '',
            FormatString="PrintTime: %Y-%m-%d %H:%M:%S",
            Bolder=False,
            AlignmentFlag=Qt.AlignRight,
            Font=self.font_YaHei_8)
        self.DataSource = [
            cur_tab.getRowValueDict(i) for i in range(len(cur_tab))
        ]

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        return False
