from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from PyQt5.QtPrintSupport import QPrinter
from lib.JPPrint.JPPrintReport import JPPrintSectionType, JPReport
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtCore import Qt
from lib.JPDatabase.Database import JPDb
from configparser import ConfigParser
from lib.JPPublc import JPPub


class PrintOrder_report_Mob(JPReport):
    def __init__(self,
                 PaperSize=QPrinter.A5,
                 Orientation=QPrinter.Orientation(1)):
        super().__init__(PaperSize, Orientation)
        self.SetMargins(30, 60, 30, 20)
        self.CopyInfo = JPPub().getCopysInfo('BillCopys_PrintingOrder')
        self.Copys = len(self.CopyInfo)
        self.logo = JPPub().MainForm.logoPixmap
        #self.logo = QPixmap(getcwd() + "\\res\\tmLogo100.png")
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

        self.Arial_Black = QFont("Arial Black")
        self.Arial_Black.setPointSize(8)
        self.Arial_Black.setBold(True)

    def init_ReportHeader_title(self,
                                title1="NOTA DE PAGAMENTO",
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
                       AlignmentFlag=(Qt.AlignTop | Qt.AlignHCenter
                                      | Qt.AlignHCenter),
                       Bolder=False)

    def init_ReportHeader(self):
        # 第1行
        RH = self.ReportHeader
        RH.AddItemRect(1, (0, 55, 90, 20),
                       "订单日期Date",
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
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 75, 90, 20),
                       "销售Vendedor:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 75, 160, 20),
                       "fVendedor",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        # 第3行
        RH.AddItemRect(1, (0, 95, 90, 20),
                       "税号NUIT:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 95, 310, 20),
                       "fNUIT",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 95, 90, 20),
                       "城市City:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 95, 160, 20),
                       "fCity",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        # 第4行
        RH.AddItemRect(1, (0, 115, 90, 20),
                       "地址Endereco:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 115, 310, 20),
                       "fEndereco",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 115, 90, 20),
                       "电子邮件Email:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (490, 115, 160, 20),
                       "fEmail",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        # 第5行
        RH.AddItemRect(1, (0, 135, 90, 20),
                       "联系人Contato:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 135, 150, 20),
                       "fContato",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (240, 135, 80, 20),
                       "手机Celular:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (320, 135, 80, 20),
                       "fCelular",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 135, 130, 20),
                       "电话Telefone:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (530, 135, 120, 20),
                       "fTelefone",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")

        # 第6行
        RH.AddItemRect(1, (0, 155, 90, 20),
                       "类别Especie:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 155, 150, 20),
                       "fEspecie",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (240, 155, 80, 20),
                       "数量Quant:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (320, 155, 80, 20),
                       "fQuant",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 155, 130, 20),
                       "单价Price:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (530, 155, 120, 20),
                       "fPrice",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       FormatString='{:,.2f} ')

        # 第7行
        RH.AddItemRect(1, (0, 175, 90, 20),
                       "每页序号Avista:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 175, 150, 20),
                       "fAvista",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (240, 175, 80, 20),
                       "联数Nr.Copy:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (320, 175, 80, 20),
                       "fNrCopy",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (400, 175, 130, 20),
                       "每本页数 Page/Vol:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (530, 175, 40, 20),
                       "fPagePerVolumn",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(3, (570, 175, 80, 20),
                       "fLogo1",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" Logo: {}")

        # 第8行
        RH.AddItemRect(1, (0, 195, 90, 20),
                       "尺寸Tamanho:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (90, 195, 90, 20),
                       "fTamanho",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")
        RH.AddItemRect(1, (180, 195, 140, 20),
                       "起始号码Numeracao:",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=Qt.AlignCenter)
        RH.AddItemRect(3, (320, 195, 330, 20),
                       "Numeracao",
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter),
                       FormatString=" {}")

        # 联次信息
        tempItem = RH.AddItemRect(1, (655, 60, 120, 20),
                                  " CONT.  / PRDUCAO",
                                  Bolder=False,
                                  Transform=True,
                                  Font=self.font_YaHei_8,
                                  AlignmentFlag=(Qt.AlignLeft
                                                 | Qt.AlignVCenter))

    def init_PageHeader(self,
                        title1="NOTA DE PAGAMENTO",
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
                       "订单日期Date",
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
                       "订单号码Nº",
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
            20, [
                "#", "数量Qtd", "名称Descrição", "长Comp.", "宽Larg.",
                "单价P. Unitario", "金额Total"
            ], [40, 50, 280, 60, 60, 80, 80], [
                Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter,
                Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter
            ],
            Font=self.font_YaHei_8,
            FillColor=self.FillColor)

    def init_ReportFooter(self):
        RF = self.ReportFooter
        RF.AddItemRect(3, (0, 0, 430, 80),
                       "fNote1",
                       FormatString='备注Note:\n{}',
                       Font=self.font_YaHei_8,
                       AlignmentFlag=(Qt.AlignLeft | Qt.AlignVCenter))
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

        # 签字部分
        RF.AddItemRect(1, (0, 95, 100, 20),
                       '制作人 Productor:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (100, 110, 100, 0), '')
        RF.AddItemRect(1, (220, 95, 100, 20),
                       '审核人 Aprovar:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (320, 110, 100, 0), '')
        RF.AddItemRect(1, (420, 95, 120, 20),
                       '会计Caixa:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (540, 110, 100, 0), '')
        RF.AddItemRect(1, (420, 125, 120, 20),
                       '客户cliente:',
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignRight | Qt.AlignVCenter),
                       Font=self.font_YaHei_8)
        RF.AddItemRect(1, (540, 140, 100, 0), '')
        noteStr = JPPub().ConfigData()['Note_PrintingOrder']
        RF.AddItemRect(1, (0, 130, 650, 60),
                       noteStr,
                       Bolder=False,
                       AlignmentFlag=(Qt.AlignLeft | Qt.TextWordWrap),
                       Font=self.Arial_Black)
        self.PageFooter.AddItemRect(4, (10, 0, 100, 20),
                                    '',
                                    FormatString='Page: {Page}/{Pages}',
                                    Bolder=False,
                                    AlignmentFlag=(Qt.AlignLeft
                                                   | Qt.AlignVCenter),
                                    Font=self.font_YaHei_8)
        self.PageFooter.AddItemRect(
            5, (110, 0, 540, 20),
            '',
            FormatString="PrintTime: %Y-%m-%d %H:%M:%S",
            Bolder=False,
            AlignmentFlag=(Qt.AlignRight
                           | Qt.AlignVCenter),
            Font=self.font_YaHei_8)

    # 修改联次
    def onBeforePrint(self, Copys, Sec, CurrentPrintDataRow, obj):
        title = self.CopyInfo[Copys - 1]['title']
        flag = self.CopyInfo[Copys - 1]['flag']
        if obj.PrintObject == " CONT.  / PRDUCAO":
            return False, title
        else:
            if obj.PrintObject in [
                    "fPrice", "fAmountDetail", "fAmount", "fDesconto", "fTax",
                    "fPayable"
            ]:
                return False, ' ' if flag is False else None
            return False, None

    def init_data(self, OrderID: str):
        SQL = """
        SELECT o.*, if(not isnull(fNumerBegin) and not 
        isnull(fNumerBegin), concat(fNumerBegin , 
        ' VIE ' ,fNumerEnd),'') AS Numeracao,
        if(isnull(fNote),' ',fNote) as fNote1 
        FROM v_order o  WHERE o.fOrderID ='{}'"""
        db = JPDb()
        data = db.getDict(SQL.format(OrderID))
        data.sort(key=lambda x: (x['fCustomerName'], x['fCity'], x['fAmount']
                                 is None, x['fAmount']))
        self.DataSource = data
