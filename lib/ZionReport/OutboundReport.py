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


class Outbound_Order_Report(JPReport):
    def __init__(self,
                 PaperSize=QPrinter.A5,
                 Orientation=QPrinter.Orientation(1)):
        super().__init__(PaperSize, Orientation)

        self.SetMargins(30, 60, 30, 30)
        self.CopyInfo = JPPub().getCopysInfo('BillCopys_OutboundOrder')
        self.Copys = len(self.CopyInfo)
        self.logo = JPPub().MainForm.logoPixmap
        self.FillColor = JPPub().getConfigData(
        )['PrintHighlightBackgroundColor']

        self.font_Algerian = QFont("Algerian")
        self.font_Algerian_11 = QFont(self.font_Algerian)
        self.font_Algerian_12 = QFont(self.font_Algerian)
        self.font_Algerian_11.setPointSize(11)
        self.font_Algerian_12.setPointSize(12)

        self.font_YaHei = QFont("微软雅黑")
        self.font_YaHei_8 = QFont(self.font_YaHei)
        self.font_YaHei_8.setPointSize(8)

        self.font_YaHei_10 = QFont(self.font_YaHei)
        self.font_YaHei_10.setPointSize(10)
        self.font_YaHei_10.setBold(True)

    def init_ReportHeader_title(self,
                                title1="Outbound Order",
                                title2="(ESTE DOCUMENTO É DO USO INTERNO)"):
        RH = self.ReportHeader
        RH.AddItemRect(2, (0, 0, 274, 50), self.logo)
        RH.AddItemRect(1, (274, 0, 400, 25),
                       title1,
                       Font=self.font_Algerian_12,
                       AlignmentFlag=(Qt.AlignCenter),
                       Bolder=False)
        RH.AddItemRect(1, (274, 25, 400, 25),
                       title2,
                       Font=self.font_Algerian_11,
                       AlignmentFlag=(Qt.AlignTop | Qt.AlignHCenter),
                       Bolder=False)

    def init_ReportHeader(self):
        # 第1行
        RH = self.ReportHeader
        RH.AddItemRect(1, (0, 55, 90, 20),
                       "出库单日期Date",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 55, 90, 20),
                       "fOrderDate",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(1, (180, 55, 130, 20),
                       "交货日期Delivery date:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (310, 55, 90, 20),
                       "fRequiredDeliveryDate",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(1, (400, 55, 90, 20),
                       "订单号码Nº",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 55, 160, 20),
                       "fOrderID",
                       Font=self.font_YaHei_10,
                       AlignmentFlag=Qt.AlignCenter)
        # 第2行
        RH.AddItemRect(1, (0, 75, 90, 20),
                       "客户Cliente:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 75, 310, 20),
                       "fCustomerName",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 75, 90, 20),
                       "销售Vendedor:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 75, 160, 20),
                       "fVendedor",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        # 第3行
        RH.AddItemRect(1, (0, 95, 90, 20),
                       "地址Endereco:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 95, 310, 20),
                       "fEndereco",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 95, 90, 20),
                       "税号NUIT:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 95, 160, 20),
                       "fNUIT",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")

        # 第4行
        RH.AddItemRect(1, (0, 115, 90, 20),
                       "电子邮件Email:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 115, 310, 20),
                       "fEmail",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")

        RH.AddItemRect(1, (400, 115, 90, 20),
                       "城市City:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 115, 160, 20),
                       "fCity",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")

        # 第5行
        RH.AddItemRect(1, (0, 135, 90, 20),
                       "联系人Contato:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 135, 90, 20),
                       "fContato",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        RH.AddItemRect(1, (180, 135, 130, 20),
                       "手机Celular:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (310, 135, 90, 20),
                       "fCelular",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 135, 90, 20),
                       "电话Telefone",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 135, 160, 20),
                       "fTelefone",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft | Qt.AlignVCenter,
                       FormatString=" {}")
        # 联次信息
        RH.AddItemRect(1, (655, 60, 120, 20),
                       " CONT.  / PRDUCAO",
                       Bolder=False,
                       Transform=True,
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignLeft)

    def init_ReportHeader_Individualization(self):
        # 第6行 Order个性部分
        RH = self.ReportHeader
        RH.AddPrintLables(
            0,
            155,
            20, ["#", "名称Descrição", "数量Qtd", "单价P. Unitario", "金额Total"],
            [40, 370, 80, 80, 80], [
                Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter,
                Qt.AlignCenter
            ],
            FillColor=self.FillColor,
            Font=self.font_YaHei_8)

    def init_PageHeader(self,
                        title1="Outbound Order",
                        title2="(ESTE DOCUMENTO É DO USO INTERNO)"):
        PH = self.PageHeader
        PH.AddItemRect(2, (0, 0, 274, 50), self.logo)
        font_title = QFont("Algerian", 12)
        font_title.setBold(True)
        PH.AddItemRect(1, (274, 0, 400, 25),
                       title1,
                       Font=self.font_Algerian_12,
                       AlignmentFlag=(Qt.AlignCenter),
                       Bolder=False)
        PH.AddItemRect(1, (274, 25, 400, 25),
                       title2,
                       Font=self.font_Algerian_11,
                       AlignmentFlag=(Qt.AlignTop | Qt.AlignVCenter
                                      | Qt.AlignHCenter),
                       Bolder=False)
        # 第1行
        PH.AddItemRect(1, (0, 55, 90, 20),
                       "出库单日期Date",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        PH.AddItemRect(3, (90, 55, 90, 20),
                       "fOrderDate",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        PH.AddItemRect(1, (180, 55, 130, 20),
                       "交货日期Delivery date:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        PH.AddItemRect(3, (310, 55, 90, 20),
                       "fRequiredDeliveryDate",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        self.font_YaHei_10.setBold(True)
        PH.AddItemRect(1, (400, 55, 90, 20),
                       "出库单号码Nº",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        PH.AddItemRect(3, (490, 55, 160, 20),
                       "fOrderID",
                       Font=self.font_YaHei_10,
                       AlignmentFlag=Qt.AlignCenter)
        # 第2行
        PH.AddPrintLables(
            0,
            75,
            20, ["#", "名称Descrição", "数量Qtd", "单价P. Unitario", "金额Total"],
            [40, 370, 80, 80, 80], [
                Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter,
                Qt.AlignCenter
            ],
            Font=self.font_YaHei_8,
            FillColor=self.FillColor)

    def init_Detail(self):
        D = self.Detail
        D.AddPrintFields(0,
                         0,
                         20, ["fQuant", "fProductName"], [40, 370],
                         [Qt.AlignCenter, Qt.AlignLeft],
                         Font=self.font_YaHei_8)
        D.AddPrintFields(410,
                         0,
                         20, ["fQuant", "fPrice"], [80, 80],
                         [(Qt.AlignRight | Qt.AlignVCenter),
                          (Qt.AlignRight | Qt.AlignVCenter)],
                         Font=self.font_YaHei_8,
                         FormatString='{:,.3f} ')
        D.AddPrintFields(570,
                         0,
                         20, ["fAmount_detail"], [80],
                         [(Qt.AlignRight | Qt.AlignVCenter)],
                         Font=self.font_YaHei_8,
                         FormatString='{:,.2f} ')
        # D.AddItem(3,
        #           40 + 50 + 280 + 60 + 60 + 80,
        #           0,
        #           80,
        #           20,
        #           "fAmountDetail",
        #           Font=self.font_YaHei_8,
        #           FormatString='{:,.3f} ',
        #           AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter))

    def init_ReportFooter(self):
        RF = self.ReportFooter
        RF.AddItemRect(1, (430, 0, 140, 20),
                       "金额合计SubTotal:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter))
        RF.AddItemRect(3, (570, 0, 80, 20),
                       "fAmount",
                       FormatString='{:,.2f} ',
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 20, 140, 20),
                       "折扣Desconto:",
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(3, (570, 20, 80, 20),
                       "fDesconto",
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       FormatString='{:,.2f} ',
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 40, 140, 20),
                       "税金IVA:",
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(3, (570, 40, 80, 20),
                       "fTax",
                       FormatString='{:,.2f} ',
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (430, 60, 140, 20),
                       "应付金额Valor a Pagar:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter))
        RF.AddItemRect(3, (570, 60, 80, 20),
                       "fPayable",
                       FormatString='{:,.2f} ',
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
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
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (100, 125, 100, 0), '')
        RF.AddItemRect(1, (220, 110, 100, 20),
                       '审核人 Aprovar:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (320, 125, 100, 0), '')
        RF.AddItemRect(1, (420, 110, 120, 20),
                       '会计Caixa:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)

        RF.AddItemRect(1, (540, 125, 100, 0), '')
        RF.AddItemRect(1, (420, 140, 120, 20),
                       '客户cliente:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)

        RF.AddItemRect(1, (540, 155, 100, 0), '')

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
            AlignmentFlag=(Qt.AlignRight
                           | Qt.AlignVCenter),
            Font=self.font_YaHei_8)

    def init_data(self, OrderID: str):
        SQL = f"""SELECT 
            o.fOrderID, o.fOrderDate, o.fRequiredDeliveryDate
            , o.fCustomerName, o.fNUIT
            , o.fCity, o.fEndereco, o.fEmail
            , o.fContato, o.fCelular
            , o.fTelefone, o.fAmount
            , o.fTax, o.fPayable, o.fDesconto
            , o.fVendedor,
            d.fQuant,
            d.fProductID,
            d.fPrice ,
            d.fAmount as fAmount_detail,
            if(isnull(o.fNote),' ',o.fNote) AS fNote1
            FROM v_product_outbound_order o
            RIGHT JOIN t_product_outbound_order_detail d
                ON o.fOrderID = d.fOrderID
            WHERE d.fOrderID='{OrderID}'
            """

        db = JPDb()
        data = db.getDict(SQL)
        data.sort(key=lambda x: (x['fCustomerName'], x['fCity'], x['fAmount']
                                 is None, x['fAmount']))
        self.DataSource = data

    # 修改联次
    def onBeforePrint(self, Copys, Sec, CurrentPrintDataRow, obj):
        #print(str(CurrentPrintDataRow))
        title = self.CopyInfo[Copys - 1]['title']
        flag = self.CopyInfo[Copys - 1]['flag']
        if obj.PrintObject == " CONT.  / PRDUCAO":
            return False, title
        elif obj.PrintObject == 'fProductName':
            return False, self.getFullProductName(
                CurrentPrintDataRow['fProductID'])
        else:
            if obj.PrintObject in [
                    "fPrice", "fAmount_detail", "fAmount", "fDesconto", "fTax",
                    "fPayable"
            ]:
                return False, ' ' if flag is False else None
            return False, None

    def BeginPrint(self, OrderID: str):
        # 大于9行自动更改纸型
        self.init_data(OrderID)
        if len(self.DataSource) > 5:
            self.PaperSize = QPrinter.A4
            self.Orientation = QPrinter.Orientation(0)
        return self.PrintCurrentReport(OrderID)

    def onFormat(self, SectionType, CurrentPage, RowDate=None):
        if (SectionType == JPPrintSectionType.PageHeader and CurrentPage == 1):
            return True

    def PrintCurrentReport(self, OrderID: str):
        self.init_ReportHeader_title(
            title1=" Outbound Order",
            title2="(ESTE DOCUMENTO É DO USO INTERNO)")
        self.init_ReportHeader()
        self.init_ReportHeader_Individualization()
        self.init_PageHeader()
        self.init_Detail()
        self.init_ReportFooter()
        super().BeginPrint()
