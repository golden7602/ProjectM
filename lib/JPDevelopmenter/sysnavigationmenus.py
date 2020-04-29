import sys
from pickle import dumps, loads
from base64 import b64decode, b64encode
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

#from lib.JPDevelopmenter.Ui.Ui_FormSysnavigationMenus import Ui_Dialog
from lib.JPDatabase.Database import JPDb, JPDbType

from PyQt5.QtWidgets import (QDialog, QApplication, QTreeWidgetItem,
                             QStyledItemDelegate)
from PyQt5.QtCore import Qt, QThread, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QIcon
from lib.JPDatabase.Query import JPQueryFieldInfo
from PyQt5 import QtCore, QtGui, QtWidgets

import json


class myTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, e):
        print(e.mimeData().hasText())
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        print(e.mimeData().text())
        #self.addItem(e.mimeData().text())

    def mimeData(self, TreeWidgetItem):
        d = QtCore.QMimeData()
        txt = json.dumps(TreeWidgetItem[0].jpData)
        d.setText(txt)
        return d


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(892, 636)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeWidget = myTreeWidget(Dialog)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.treeWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel
                                          | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "SysNavigationMenus"))


class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.SQL = """
            SELECT fMenuText, fEnabled, fDefault, fIcon, fNodeBackvolor
                , fNodeForeColor, fNodeFontBold, fExpanded, fNMID, fDispIndex
                , fParentId, fIsCommandButton, fCommand, fObjectName, fFormMode
                , fArg, fDescription, fLevel
            FROM sysnavigationmenus
            ORDER BY fDispIndex
            """
        self.tableInfo = JPQueryFieldInfo(self.SQL)

    def rowCount(self, parent=QModelIndex()):
        return len(self.tableInfo)

    def columnCount(self, parent=QModelIndex()):
        return len(self.tableInfo.Fields)

    def data(self, Index, role=Qt.DisplayRole):
        r = Index.row()
        c = Index.column()
        if role == Qt.DisplayRole:
            return self.tableInfo.getOnlyData([r, c])

    def setData(self, QModelIndex, Any, role=Qt.EditRole):
        return super().setData(QModelIndex, Any, role=role)

    def parent(self, QModelIndex):
        return super().parent(QModelIndex)

    def headerData(self, int, QtOrientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and QtOrientation == Qt.Horizontal:
            return 'Col' + str(int)
        #return super().headerData(int, QtOrientation, role=role)


def loadTreeview(treeWidget, items):
    class MyThreadReadTree(QThread):  # 加载功能树的线程类
        def __init__(self, treeWidget, items):
            super().__init__()
            treeWidget.clear()
            root = QTreeWidgetItem(treeWidget)
            root.setText(0, "Function")
            root.FullPath = "Function"
            self.root = root
            self.items = items
            self.icopath = getcwd() + "\\res\\ico\\{}"

        def addItems(self, parent, items):
            for r in items:
                item = QTreeWidgetItem(parent)
                item.setText(0, r["fMenuText"])
                item.setText(1, str(r["fDispIndex"]))
                item.setText(2, str(r["fIcon"]))
                item.setCheckState(3, r["fDefault"])
                #item.setText(3, str(r["fDefault"]))
                item.setText(4, str(r["fNodeBackvolor"]))
                item.setText(5, str(r["fNodeForeColor"]))
                item.setText(6, str(r["fNodeFontBold"]))
                #print(self.icopath.format(r["fIcon"]))
                item.setIcon(0, QIcon(self.icopath.format(r["fIcon"])))
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

    _readTree = MyThreadReadTree(treeWidget, items)
    _readTree.run()


class myQStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)


class Edit_FormSysnavigationMenus(QDialog):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        #self.ui.treeView.setModel(TreeModel())

        # self.ui.treeWidget.setItemDelegateForColumn()
        self.ui.treeWidget.setColumnCount(18)
        self.ui.treeWidget.setHeaderLabels([
            '显示文本', '显示顺序', '图标', '默认权限', '前景色', '背景色', 'fObjectName',
            'fFormMode', 'fArg', 'fIcon', 'fDefault', 'fNodeBackvolor',
            'fNodeForeColor', 'fNodeFontBold', 'fExpanded', 'fDescription',
            'fLevel', 'fIsCommandButton'
        ])
        self.SQL = """
            SELECT fNMID, fDispIndex, fParentId, fEnabled, fMenuText
                , fCommand, fObjectName, fFormMode, fArg, fIcon
                , fDefault, fNodeBackvolor, fNodeForeColor, fNodeFontBold, fExpanded
                , fDescription, fLevel, fIsCommandButton
            FROM sysnavigationmenus
            ORDER BY fDispIndex
            """
        db = JPDb()
        lst = db.getDict(self.SQL)
        loadTreeview(self.ui.treeWidget, lst)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setStyle('Fusion')
    app = QApplication(sys.argv)
    db = JPDb()
    db.setDatabaseType(JPDbType.MySQL)
    fld = Edit_FormSysnavigationMenus()
    # fld.ui.splitter.setStretchFactor(0, 2)
    # fld.ui.splitter.setStretchFactor(1, 11)
    fld.showMaximized()
    sys.exit(app.exec_())
