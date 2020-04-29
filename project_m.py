#!/usr/bin/python
# -*- coding: UTF-8 -*-

from os import getcwd, environ, path as ospath
from sys import argv
from sys import exit as sys_exit
from sys import path as jppath

# 下面行解决造生成exe后闪退，请不要注释或删除
# 命令行下运行出现如下提示
# ImportError: unable to find Qt5Core.dll on PATHImportError: unable to find Qt5Core.dll on PATH
# 的问题
import fix_qt_import_error

from PyQt5 import sip
from PyQt5.QtCore import QMetaObject, Qt, QThread
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QProgressBar, QPushButton, QTreeWidgetItem,
                             QWidget)

from lib.JPDatabase.Database import JPDb, JPDbType
from lib.JPFunction import readQss, setWidgetIconByName, seWindowsIcon
from lib.JPPublc import JPPub, JPUser
from lib.ZionWidgets.Adjustment import JPFuncForm_Adjustment
from lib.ZionWidgets.Background import Form_Background
from lib.ZionWidgets.Backup import Form_Backup
from lib.ZionWidgets.Complete import JPFuncForm_Complete
from lib.ZionWidgets.config import Form_Config
from lib.ZionWidgets.Customer import Form_Customer
from lib.ZionWidgets.Customer_Arrears import Form_FormCustomer_Arrears
from lib.ZionWidgets.EnumManger import Form_EnumManger
from lib.ZionWidgets.Order import JPFuncForm_Order
from lib.ZionWidgets.Payment import JPFuncForm_Payment
from lib.ZionWidgets.PrintingOrder import JPFuncForm_PrintingOrder
from lib.ZionWidgets.PrintingQuotation import JPFuncForm_PrintingQuotation
from lib.ZionWidgets.Quotation import JPFuncForm_Quotation
from lib.ZionWidgets.Receivables import Form_Receivables
from lib.ZionWidgets.Report_Day import Form_Repoet_Day
from lib.ZionWidgets.User import Form_User
from lib.ZionWidgets.OutboundOrder import JPFuncForm_OutboundOrder
from lib.ZionWidgets.WarehouseReceipt import JPFuncForm_WarehouseReceipt
from lib.ZionWidgets.ProductInformation import Form_ProductList
from lib.ZionWidgets.Supplier import Form_Supplier
from lib.ZionWidgets.ProductInOutDetails import Form_product_in_out_detail
from Ui.Ui_FormMain import Ui_MainWindow
from lib.JPConfigInfo import ConfigInfo


def loadTreeview(treeWidget, items, MF):
    class MyThreadReadTree(QThread):  # 加载功能树的线程类
        def __init__(self, treeWidget, items, MF):
            super().__init__()
            treeWidget.clear()
            root = QTreeWidgetItem(treeWidget)
            root.setText(0, "Function")
            root.FullPath = "Function"
            self.root = root
            self.items = items
            self.icoPath = MF.icoPath

        def addItems(self, parent, items):
            for r in items:
                item = QTreeWidgetItem(parent)
                item.setText(0, r["fMenuText"])
                item.setIcon(0, QIcon(self.icoPath.format(r["fIcon"])))
                item.jpData = r
                item.FullPath = (parent.FullPath + '\\' + r["fMenuText"])
                lst = [l for l in self.items if l["fParentId"] == r["fNMID"]]
                self.addItems(item, lst)
                item.setExpanded(1)

        def run(self):  # 线程执行函数
            lst = [l for l in self.items if l["fParentId"] == 1]
            self.addItems(self.root, lst)
            self.root.setExpanded(True)

        def getRoot(self):
            return

    _readTree = MyThreadReadTree(treeWidget, items, MF)
    _readTree.run()


class JPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        JPPub().MainForm = self
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label_Title.setText("Project_M")
        #self.ui.label_Title.setText("ColorPro OrderM")
        #self.setWindowTitle("ColorPro OrderM")
        self.setWindowTitle("Project_M")

        # self.icoPath = ":/pic/res/ico/{}"
        # self.logoPath = ":/logo/res/{}"
        self.icoPath = getcwd() + "\\res\\ico\\{}"
        self.logoPath = getcwd() + "\\res\\{}"

        # 设置主窗体中按钮图标及Logo
        self.logoPixmap = QPixmap(self.logoPath.format("zions_100.png"))
        self.backPixmap = QPixmap(self.logoPath.format("zions_tm.png"))
        self.addOneButtonIcon(self.ui.ChangeUser, "changeuser.png")
        self.addOneButtonIcon(self.ui.ChangePassword, "changepassword.png")
        self.addLogoToLabel(self.ui.label_logo)

        # 用户及密码修改功能
        objUser = JPUser()
        objUser.INIT()  # 程序开始时只初始化一次
        objUser.userChange.connect(self.onUserChanged)
        objUser.currentUserID()
        self.ui.ChangeUser.clicked.connect(objUser.changeUser)
        self.ui.ChangePassword.clicked.connect(objUser.changePassword)

        # 堆叠布局
        self.ui.stackedWidget.removeWidget(self.ui.page)
        self.ui.stackedWidget.removeWidget(self.ui.page_2)

        # 隐藏树标题
        self.ui.label_FunPath.setText('')
        self.ui.treeWidget.setHeaderHidden(True)

        # 设置状态条中的进度条及标签
        self.Label = QLabel("")
        self.ProgressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.Label)
        self.statusBar().addPermanentWidget(self.ProgressBar)
        self.ProgressBar.hide()

        # 连接点击了功能树中的节点到函数
        self.ui.treeWidget.itemClicked[QTreeWidgetItem, int].connect(
            self.treeViewItemClicked)

    def treeViewItemClicked(self, item, i):
        # 当点击了功能树中的节点时
        try:
            self.ui.label_FunPath.setText(item.FullPath)
            self.getStackedWidget(item.jpData)
        except AttributeError as e:
            print(str(e))

    def onUserChanged(self, args):
        self.ui.label_UserName.setText(args[1])
        loadTreeview(self.ui.treeWidget, JPUser().currentUserRight(), self)
        Form_Background(self)

    def addForm(self, form):
        st = self.ui.stackedWidget
        if st.count() > 0:
            temp = st.widget(0)
            st.removeWidget(temp)
            try:
                JPPub().UserSaveData.disconnect(temp.UserSaveData)
            except Exception:
                pass
            del temp
        st.addWidget(form)

    def getTaxCerPixmap(self, fn):
        # 税务登记证件保存路径
        toPath = JPPub().ConfigData()['TaxRegCerPath']
        fn_m = f'{toPath}\\{fn}'
        if ospath.exists(fn_m):
            return QPixmap(fn_m)
        else:
            e = FileExistsError()
            e.Msg = f'File "{fn_m}" do not exists!'
            raise e

    def getIcon(self, icoName):
        return QIcon(self.icoPath.format(icoName))

    def getPixmap(self, icoName):
        return QPixmap(self.icoPath.format(icoName))

    def addOneButtonIcon(self, btn, icoName):
        icon = QIcon(self.icoPath.format(icoName))
        btn.setIcon(icon)

    def addLogoToLabel(self, label):
        label.setPixmap(self.logoPixmap)

    def addButtons(self, frm, btns):
        layout = frm.findChild((QHBoxLayout, QWidget), 'Layout_Button')
        layout.setSpacing(2)
        if not (layout is None):
            for m in btns:
                btn = QPushButton(m['fMenuText'])
                btn.NMID = m['fNMID']
                btn.setObjectName(m['fObjectName'])
                self.addOneButtonIcon(btn, m['fIcon'])
                btn.setEnabled(m['fHasRight'])
                layout.addWidget(btn)
            QMetaObject.connectSlotsByName(frm)

    def getStackedWidget(self, sysnavigationmenus_data):
        frm = None
        btns = sysnavigationmenus_data['btns']
        self.menu_id = sysnavigationmenus_data['fNMID']
        form_createor = {
            2: JPFuncForm_Order,
            9: JPFuncForm_Payment,
            15: JPFuncForm_Complete,
            14: Form_Config,
            18: JPFuncForm_Adjustment,
            56: JPFuncForm_Quotation,
            55: JPFuncForm_PrintingQuotation,
            72: JPFuncForm_PrintingOrder,
            22: Form_Repoet_Day,
            10: Form_EnumManger,
            20: Form_Receivables,
            73: Form_Customer,
            13: Form_User,
            148: Form_FormCustomer_Arrears,
            147: Form_Backup,
            152: JPFuncForm_OutboundOrder,
            160: JPFuncForm_WarehouseReceipt,
            168: Form_ProductList,
            176: Form_Supplier,
            186: Form_product_in_out_detail
        }
        if self.menu_id == 12:
            self.close()
        elif self.menu_id in form_createor:
            frm = form_createor[self.menu_id](self)
        else:
            frm = Form_Background(self)

        # 尝试给窗体添加按钮,要求窗体中有一个名为 “Layout_Button”的布局
        self.addButtons(frm, btns)
        return

    def closeEvent(self, *args):
        # 关闭主窗体前先关闭数据库游标
        JPDb().close()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setStyle('Fusion')
    app = QApplication(argv)
    db = JPDb()
    db.setDatabaseType(JPDbType.MySQL)
    MainWindow = JPMainWindow()
    icon = QIcon()
    icon.addPixmap(
        QPixmap(MainWindow.icoPath.format("medical_invoice_information.png")))
    MainWindow.setWindowIcon(icon)
    MainWindow.ui.splitter.setStretchFactor(0, 2)
    MainWindow.ui.splitter.setStretchFactor(1, 11)
    # 启动数据改变事件的监听
    JPPub().receiveMessage(app)
    MainWindow.showMaximized()
    sys_exit(app.exec_())
