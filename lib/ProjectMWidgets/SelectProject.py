from PyQt5.QtWidgets import (
    QTreeWidgetItem, QWidget, QDialog, QTreeWidgetItemIterator)
from PyQt5.QtCore import (QMetaObject, Qt, pyqtSlot,
                          QThread, QModelIndex, pyqtSignal, QObject)
from PyQt5.QtGui import QBrush, QColor
from Ui.Ui_FormSelectProject import Ui_Form
from lib.JPPublc import JPDb, JPPub
import os
import re
from sys import path as jppath
jppath.append(os.getcwd())


def loadTreeview(treeWidget, items, selected_project):
    class MyThreadReadTree(QThread):
        """加载功能树的线程类"""

        def __init__(self, treeWidget, items):
            super().__init__()
            treeWidget.clear()
            tree_title = ["项目列表", "选择"]
            treeWidget.setHeaderLabels(tree_title)
            treeWidget.dirty = False
            root = QTreeWidgetItem(treeWidget)
            root.setText(0, "高科集团")
            root.FullPath = "高科集团"
            root.key = "ORG000"
            root.dirty = False
            treeWidget._rootItem = root
            self.root = root
            self.items = items
            self.selected_project = selected_project
            #self.icopath = JPPub().MainForm.icoPath

        def parentChecked(self, parentItem: QTreeWidgetItem):
            parentItem.setExpanded(1)
            if parentItem.key == self.root.key:
                return
            else:
                self.parentChecked(parentItem.parent())

        def addItems(self, parent, items):
            for r in items:
                item = QTreeWidgetItem(parent)
                item.setText(0, r["nm"])
                item.key = r['pk']
                if r['pk'][0:3] != 'ORG':
                    if r["pk"] in self.selected_project:
                        item.setCheckState(1, Qt.Checked)
                        self.parentChecked(item.parent())
                    else:
                        item.setCheckState(1, Qt.Unchecked)
                item.jpData = r
                item.dirty = False
                item.FullPath = (parent.FullPath + '\\' + r["nm"])
                self.addItems(
                    item,
                    [l for l in self.items if l["par"] == r["pk"]])

                # item.setExpanded(1)

        def run(self):  # 线程执行函数
            self.addItems(self.root,
                          [l for l in self.items if l["par"] == "ORG000"])
            self.root.setExpanded(True)

        def getRoot(self):
            return
    _readTree = MyThreadReadTree(treeWidget, items)
    _readTree.run()


class FormSelectProject(Ui_Form, QObject):
    selectItemChanged = pyqtSignal(list)

    def __init__(self, selected_project=[]):
        super().__init__()
        self.ListWidget = None
        # self.buttonBox.accepted.connect(self.okClick)
        sql = "Select pk,nm,par from v_project_tree order by pk"
        tree_data = JPDb().getDict(sql)
        self.Dialog = QDialog()
        self.setupUi(self.Dialog)
        self.Dialog.setWindowModality(Qt.ApplicationModal)
        self.treeWidget.setColumnWidth(0, 450)
        self.lineEdit.textChanged.connect(self.actionClick)
        loadTreeview(self.treeWidget, tree_data, selected_project)
        self.butOK.clicked.connect(self.okClicked)
        self.butCancel.clicked.connect(self.onCancelClick)
        #self.Dialog.accept = self.okClick

    def show(self):
        return self.Dialog.exec_()

    def onCancelClick(self):
        self.Dialog.close()

    def setListWidget(self, ListWidget):
        self.ListWidget = ListWidget

    def okClicked(self):
        # 遍历树控件节点
        cursor = QTreeWidgetItemIterator(self.treeWidget)
        lst = []
        while cursor.value():
            item = cursor.value()
            if item.checkState(1) == Qt.Checked:
                lst.append(item.key)
            cursor = cursor.__iadd__(1)
        self.selectItemChanged.emit(lst)
        self.Dialog.close()

    def ChangeParentExpanded(self, item):
        """递归修改上级为选中"""
        if item.parent() is self.treeWidget._rootItem:
            return
        else:
            p = item.parent()
            if p:
                p.setExpanded(True)
                self.ChangeParentExpanded(p)

    def actionClick(self, txt):
        if not txt:
            return
        p = ''.join((r'.*', txt, r'.*'))
        obj = re.compile(p)
        cursor = QTreeWidgetItemIterator(self.treeWidget)
        while cursor.value():
            item = cursor.value()
            if item is not self.treeWidget._rootItem:
                item.setExpanded(False)
                item.setSelected(False)
            cursor = cursor.__iadd__(1)
        cursor = QTreeWidgetItemIterator(self.treeWidget)
        while cursor.value():
            item = cursor.value()
            if item is self.treeWidget._rootItem:
                cursor = cursor.__iadd__(1)
                continue
            if item.parent() is self.treeWidget._rootItem:
                cursor = cursor.__iadd__(1)
                continue
            itemtext = item.text(0)
            if obj.match(itemtext):
                self.ChangeParentExpanded(item)
                item.setSelected(True)
            cursor = cursor.__iadd__(1)
