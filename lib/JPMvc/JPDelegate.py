# -*- coding: utf-8 -*-
# @Time    : 19-12-1 下午3:26
# @Author  : JPT
# @Site    :
# @File    : JPTableModel\__init__.py
# @Software: VS Code

import abc
import datetime
import os
import sys
sys.path.append(os.getcwd())

from PyQt5.QtCore import (QAbstractItemModel, QDate, QModelIndex, QObject, Qt,
                          pyqtSignal)
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QComboBox, QDateEdit, QLineEdit, QPushButton,
                             QStyledItemDelegate, QStyleOptionViewItem,
                             QWidget)

from lib.JPDatabase.Field import JPFieldType
from lib.JPFunction import JPBooleanString, JPDateConver




class _JPDelegate_Base(QStyledItemDelegate):
    editNext = pyqtSignal(QModelIndex)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        #try:
        # 关闭中文输入法

        # except Exception as identifier:
        #     pass

    @abc.abstractmethod
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        pass

    @abc.abstractmethod
    def setEditorData(self, editor: QWidget, index: QModelIndex):
        pass

    @abc.abstractmethod
    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        pass

    def updateEditorGeometry(self, editor: QWidget,
                             StyleOptionViewItem: QStyleOptionViewItem,
                             index: QModelIndex):
        editor.setGeometry(StyleOptionViewItem.rect)


class JPDelegate_ReadOnly(_JPDelegate_Base):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return

    def setEditorData(self, editor, index):
        return

    def setModelData_(self, editor, model, index):
        return


class JPDelegate_LineEdit(_JPDelegate_Base):
    def __init__(self, parent: QObject = None, value_type=None, decimal=2):
        '''JPDelegate_LineEdit(parent: QObject = None, value_type=None, decimal)\n
        value_type 为数据类型，1整数、2小数 None或不赋值时为文本或其他值'''
        super().__init__(parent)
        self.__ValueType = value_type
        self.__Decimal = decimal

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        wdgt = QLineEdit(parent)
        wdgt.setAttribute(Qt.WA_InputMethodEnabled, False)
        if self.__ValueType == JPFieldType.Int:
            wdgt.setValidator(QIntValidator())
        if self.__ValueType == JPFieldType.Float:
            va = QDoubleValidator()
            va.setDecimals(self.__Decimal)
            wdgt.setValidator(va)
        return wdgt

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        text = index.model().data(index, Qt.EditRole)
        if text:
            editor.setText(str(text))

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        txt = editor.text()
        if txt is None:
            index.model().setData(index, None, Qt.EditRole)
            return
        v = None
        if self.__ValueType == JPFieldType.Int:
            v = int(txt.replace(",", ""))
        elif self.__ValueType == JPFieldType.Float:
            v = float(txt.replace(",", ""))
        else:
            v = txt
        index.model().setData(index, v, Qt.EditRole)


class JPDelegate_ComboBox(_JPDelegate_Base):
    def __init__(self, parent: QObject = None, RowSource=[]):
        '''JPDelegate_ComboBox(parent: QObject = None, RowSource=[])\n
        RowSource为行来源 '''
        super().__init__(parent)
        self.RowSource = RowSource

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        wdgt = QComboBox(parent)
        wdgt.setAttribute(Qt.WA_InputMethodEnabled, False)
        for row in self.RowSource:
            wdgt.addItem(row[0], row[1])
        return wdgt

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        data = index.model().data(index, Qt.EditRole)
        if data is None:
            editor.setCurrentIndex(-1)
            return
        data = ord(data) if isinstance(data, bytes) else data
        for i, row in enumerate(self.RowSource):
            if row[1] == data:
                editor.setCurrentIndex(i)
                return

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        index.model().setData(index, editor.currentData(), Qt.EditRole)


class JPDelegate_DateEdit(_JPDelegate_Base):
    def __init__(self, parent: QObject = None):
        '''JPDelegate_DateEdit(parent: QObject = None)'''
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        wdgt = QDateEdit(parent)
        wdgt.setDisplayFormat("yyyy-MM-dd")
        wdgt.setDate(datetime.date.today())
        wdgt.setCalendarPopup(True)
        return wdgt

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        data = index.model().data(index, Qt.EditRole)
        if data is None:
            return
        editor.setDate(JPDateConver(data, QDate))

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        index.model().setData(index, JPDateConver(editor.date(),
                                                  datetime.date), Qt.EditRole)
