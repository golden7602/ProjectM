# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

import re
from PyQt5.QtCore import (QAbstractTableModel, QDate, QModelIndex, QObject, Qt,
                          QVariant, pyqtSignal)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QMessageBox, QTableView

import lib.JPMvc.JPDelegate as myDe
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Field import JPFieldType
from lib.JPDatabase.Query import (JPQueryFieldInfo, JPTabelFieldInfo,
                                  JPTabelRowData)
from lib.JPFunction import (JPBooleanString, JPDateConver, JPGetDisplayText,
                            JPRound, PrintFunctionRunTime)
from lib.JPMvc import JPWidgets
from lib.JPPublc import JPPub


class JPTableViewModelBase(QAbstractTableModel):
    dataChanged = pyqtSignal(QModelIndex, object)
    firstHasDirty = pyqtSignal()
    editNext = pyqtSignal(QModelIndex)
    readingRow = pyqtSignal(int)

    def __init__(self, tabelFieldInfo: JPTabelFieldInfo = None):
        super().__init__()
        self.TabelFieldInfo = tabelFieldInfo
        self.tableView = None
        self._dirty = False
        self.__isCalculating = False
        self.__readingRow = -1




    def _setdirty(self, state: bool = True):
        # 第一次存在脏数据时，发送一个信号
        if self._dirty is False and state is True:
            self._dirty = True
            self.firstHasDirty.emit()

    @property
    def dirty(self) -> bool:
        """返回模型中是否有脏数据"""
        return self._dirty

    def setTabelFieldInfo(self, tabelFieldInfo: JPTabelFieldInfo):
        tabelFieldInfo.Data = [
            JPTabelRowData(item) for item in tabelFieldInfo.Data
        ]
        self.TabelFieldInfo = tabelFieldInfo

    def getDataDict(self, role: int = Qt.DisplayRole):
        ''''按行返回数据字典的列表,一般用于打印'''

        tab = self.TabelFieldInfo
        l = len(tab)
        if role == Qt.EditRole:
            dic = [tab.getRowValueDict(i) for i in range(l)]
            return dic
        result = []
        if role == Qt.DisplayRole:
            for r in range(l):
                temp_Dic = {}
                row_data = self.DataRows[r].Datas
                for c, data in row_data:
                    fld = tab.Fields[c]
                    txt = JPGetDisplayText(data, FieldInfo=fld)
                    temp_Dic[fld.FieldName] = txt
                result.append(temp_Dic)
            #r = {k: JPGetDisplayText(v) for k, v in dic.items()}
        return result

    def __getPara(self, Index):
        c = Index.column()
        return (Index.row(), c, self.TabelFieldInfo.Fields[c].FieldName,
                self.TabelFieldInfo.Fields[c].TypeCode,
                self.TabelFieldInfo.Fields[c].RowSource)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.TabelFieldInfo)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.TabelFieldInfo.Fields)

    def _GetHeaderAlignment(self, Index: QModelIndex) -> int:
        return Qt.AlignCenter

    def _getDecoration(self, Index: QModelIndex) -> QVariant():
        """返回 (QColor, QIcon or QPixmap)"""
        return QVariant()

    def data(self, Index: QModelIndex,
             role: int = Qt.DisplayRole) -> QVariant():

        c = Index.column()
        r = Index.row()
        if r != self.__readingRow:
            self.__readingRow = r
            self.readingRow.emit(r)
        tf = self.TabelFieldInfo
        if not Index.isValid():
            raise Exception("行数或列数设置有误！")
        if role == Qt.TextAlignmentRole:
            return (Qt.AlignLeft
                    | Qt.AlignVCenter
                    ) if tf.Fields[c].RowSource else tf.Fields[c].Alignment
        elif role == Qt.DisplayRole:
            return tf.getDispText(Index)
        elif role == Qt.DecorationRole:
            return self._getDecoration(Index)
        elif role == Qt.TextColorRole:
            return QColor(Qt.black)
        elif role == Qt.BackgroundColorRole:
            return QColor(Qt.white)
        elif role == Qt.EditRole:
            # r, c, fn, tp, rs = self.__getPara(Index)
            return tf.getOnlyData(Index)

    def __formulaCacu(self, row_num: int):
        # 这个可能要重新写
        rd = self.TabelFieldInfo.DataRows[row_num]
        fms = [f for f in self.TabelFieldInfo.Fields if f.Formula]
        for fld in fms:
            try:
                d = rd.Datas
                v = eval(fld.Formula.format(*d))
                self.__isCalculating = True
                rd.setData(fld._index, v)
                self.__isCalculating = False
            except Exception:
                pass

    def afterInsterRowEvent(self):
        """增加一行后执行"""
        return

    def setData(self, Index: QModelIndex, Any,
                role: int = Qt.EditRole) -> bool:
        t_inof = self.TabelFieldInfo
        t_inof.setData(Index, Any)
        self._setdirty()
        if self.__isCalculating is False:
            self.__formulaCacu(Index.row())
        # 执行重载函数，判断行数据是否合法
        # 给函数参数的值 是最后一行的数据list
        row_data = t_inof.getRowData(len(t_inof.DataRows) - 1)
        tempv = self.afterSetDataBeforeInsterRowEvent(row_data, Index)

        if isinstance(tempv, bool):
            if tempv:
                self.insertRows(self.rowCount())
                self.afterInsterRowEvent()
        else:
            strErr = 'afterSetDataBeforeInsterRowEvent函数的返回值必须为逻辑值！'
            raise TypeError(strErr)
        # 回车向右
        r, c = Index.row(), Index.column()
        tmp = None
        tmp = Index.sibling(r if r == self.rowCount() - 1 else r + 1,
                            0 if self.columnCount() - 1 else c + 1)
        if tmp.isValid():
            self.editNext.emit(tmp)
        self.dataChanged[QModelIndex, object].emit(Index, Any)
        return True

    def afterSetDataBeforeInsterRowEvent(self, row_data,
                                         Index: QModelIndex) -> True:
        '''子窗体更新数据后,执行此事件，可重载，返回值必须为逻辑值
        不重载时，默认不增加行，返回True时增加行
       '''
        return False

    def setFormula(self, key: int, formula: str):
        """
        设置计算公式 {字段名}代表一个值
        本公式也用于增加新行前的检查，也用于列间的运算
        key为列号或字段名;formula格式示例如下：
        {7}=(JPRound({1},2) + NV({2},float))/2
        列2的值转换成浮点数与列3的值转换成浮点数和的一半
        等号左边为目标字段值，右边为公式，遵照python语法
        如果可以保证公式右边字段值不包含0，也可以不使用NV函数
        NV函数为一个自定义函数，用于防止None值并转换成指定类型
        JPRound函数为一个自定义函数,四舍五入
        """
        if isinstance(key, str):
            self.FieldsDict[key].Formula = formula
        if isinstance(key, int):
            self.Fields[key].Formula = formula

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def headerData(self, section, Orientation,
                   role: int = Qt.DisplayRole) -> QVariant():
        if role != Qt.DisplayRole:
            return QVariant()
        if Orientation == Qt.Horizontal:
            flds = self.TabelFieldInfo.Fields
            return QVariant(flds[section].Title if flds[section].
                            Title else flds[section].FieldName)
        return QVariant(int(section + 1))

    def getColumnSum(self, col):
        """得到某一列的合计值"""
        tp = self.TabelFieldInfo.Fields[col].TypeCode
        rd = self.TabelFieldInfo.getOnlyData
        if tp in [tp == JPFieldType.Int, JPFieldType.Float]:
            if tp == JPFieldType.Int:
                r, con = 0, lambda v: int(v.to_eng_string())
            if tp == JPFieldType.Float:
                r, con = 0.0, lambda v: float(v.to_eng_string())
            for i in range(len(self.TabelFieldInfo.DataRows)):
                tempValue = rd([i, col])
                tempValue = tempValue if tempValue else 0
                r += tempValue
            return r
        raise TypeError("指定的列[{}]不能进行数值运算".format(col))

    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        self.TabelFieldInfo.addRow()
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.TabelFieldInfo.deleteRow(position)
        self.endRemoveRows()
        self._setdirty()
        return True

    def setColumnsDetegate(self):
        """setColumnsDetegate(TableView: QTableViewt)\n
        参数为需要设置代理的TableView控件"""
        tw = self.tableView
        if not isinstance(tw, QTableView):
            raise TypeError("setColumnsDetegate()方法有参数必须为QTableView")
        for col, fld in enumerate(self.TabelFieldInfo.Fields):
            tp = fld.TypeCode
            de = None
            if fld.RowSource:
                de = myDe.JPDelegate_ComboBox(tw, fld.RowSource)
            elif tp == JPFieldType.Int:
                de = myDe.JPDelegate_LineEdit(tw, 1)
            elif tp == JPFieldType.Float:
                de = myDe.JPDelegate_LineEdit(tw, 2, fld.Scale)
            elif tp == JPFieldType.Boolean:
                boostr = fld.RowSource if fld.RowSource else self.BooleanString
                de = myDe.JPDelegate_ComboBox(tw, boostr)
            elif tp == JPFieldType.Date:
                de = myDe.JPDelegate_DateEdit(tw)
            else:
                de = myDe.JPDelegate_LineEdit(tw)
            if de:
                tw.setItemDelegateForColumn(col, de)


class JPTableViewModelReadOnly(JPTableViewModelBase):
    def __init__(self, tableView, tabelFieldInfo: JPTabelFieldInfo):
        ''' 
        建立一个只读型模型，仅仅用于展示内容，不可编辑\n
        JPTableModelReadOnly(tableView,tabelFieldInfo:TabelFieldInfo)
        '''
        super().__init__(tabelFieldInfo)
        # 设置只读
        self.tableView = tableView
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)


class JPTableViewModelEditForm(JPTableViewModelBase):
    def __init__(self, tableView, tabelFieldInfo: JPTabelFieldInfo):
        ''' 
        建立一个可编辑模型\n
        JPTableViewModelEditForm(tableView,tabelFieldInfo:TabelFieldInfo)\n
        '''
        super().__init__(tabelFieldInfo)
        self.tableView = tableView
