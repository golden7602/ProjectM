from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from Ui.Ui_FormProductSelecer import Ui_ProductSelecer
from PyQt5.QtWidgets import QDialog, QLineEdit, QApplication
from PyQt5.QtGui import QIcon
from lib.JPPublc import JPPub
from PyQt5.QtCore import Qt, pyqtSignal
from lib.JPMvc.JPModel import JPTableViewModelReadOnly
from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPDatabase.Database import JPDb, JPDbType


class ProductSelecter(QDialog):
    ProductSeledted = pyqtSignal(int, str, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_ProductSelecer()
        self.ui.setupUi(self)
        icon = QIcon(JPPub().MainForm.icoPath.format("search.png"))
        #icon = QIcon("E:\\Zion\\zion\\res\\ico\\search.png")
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        #self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, False)
        action.triggered.connect(self.actionClick)
        self.ui.tableView.doubleClicked.connect(self.tv_doubleClicked)
        self.actionClick()

    def tv_doubleClicked(self, index1):
        r = index1.row()
        #p_id = self.tab.getOnlyData([r, 0])
        self.emitEvent(r)
        self.close()

    def accept(self):
        index = self.ui.tableView.selectionModel().currentIndex()
        r = index.row()
        if r != -1:
            self.emitEvent(r)
        self.close()

    def emitEvent(self, rowNum):
        r=rowNum
        p_id = self.tab.getOnlyData([r, 0])
        product_name = self.tab.getOnlyData([r, 1])
        fCurrentQuantity = self.tab.getOnlyData([r, 2])
        self.ProductSeledted.emit(p_id, product_name, fCurrentQuantity)

    def actionClick(self):
        key = self.ui.lineEdit.text()
        key = key if key else ''
        sql = f"""
        select 
        fID as `序号NO.`, 
        fProductName as `产品名称Descrição do produto`, 
        fCurrentQuantity as 当前库存Quantidade ,
        fSpesc as  `规格Especificação`, 
        fWidth as 宽Largura, 
        fLength as 长Longo, 
        fUint 单位Unidade, 
        fNote as 备注Observações
        from t_product_information 
        where fCancel=0 and fProductName like '%{key}%' 
        order by  fID
        """
        self.tab = JPQueryFieldInfo(sql)
        self.mod = JPTableViewModelReadOnly(self.ui.tableView, self.tab)
        self.ui.tableView.setModel(self.mod)
        self.ui.tableView.resizeColumnsToContents()


if __name__ == "__main__":
    import sys

    db = JPDb()
    db.setDatabaseType(JPDbType.MySQL)

    app = QApplication(sys.argv)
    ps = ProductSelecter()
    ps.show()

    sys.exit(app.exec_())