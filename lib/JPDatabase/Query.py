import datetime
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

import re
from copy import deepcopy
from PyQt5.QtCore import QModelIndex
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Field import JPFieldInfo
from PyQt5.QtWidgets import QMessageBox
from lib.JPFunction import JPGetDisplayText
#from lib.JPPublc import JPPub


class JPTabelRowData(object):
    New_None = -1
    New = 0
    OriginalValue = 1
    Update = 2

    def __init__(self, values_or_ColumnCount: [list, int]):
        """生成一个数据行对象
        JPTabelRowData(values_or_ColumnCount)
        参数为一个数据列表，或列数，当给定列数时，则生成一个空行对象，值全部为None
        """
        super().__init__()
        value = values_or_ColumnCount
        if isinstance(value, list):
            self.__data = value
            self._state = self.OriginalValue
        elif isinstance(value, int):
            self.__data = [None] * value
            self._state = self.New
        else:
            raise ValueError("参数值错误")

    @property
    def State(self) -> int:
        return self._state

    def Data(self, column):
        return self.__data[column]

    @property
    def Datas(self):
        return self.__data

    def setData(self, column, value):
        if self.__data[column] == value:
            return
        if self._state == self.OriginalValue:
            self._state = self.Update
        if self._state == self.New_None:
            self._state = self.New
        self.__data[column] = value


class JPQueryFieldInfo(object):
    New_None = -1
    New = 0
    OriginalValue = 1
    Update = 2

    @staticmethod
    def getRC(index: [list, tuple, QModelIndex]):
        if isinstance(index, (list, tuple)):
            if len(index) == 2:
                r, c = index
        elif isinstance(index, QModelIndex):
            r, c = index.row(), index.column()
        else:
            raise ValueError("参数错误,参数一只能为长度为2的list, tuple,或一个QModelIndex")
        return r, c

    def __init__(self, sql):
        '''返回一个只读的查询的数据信息，数据不可更改'''
        db = JPDb()
        flds, data = db.getFeildsInfoAndData(sql)
        # self.__isMain = True
        self.Fields = flds
        self.DataRows = [JPTabelRowData(row) for row in data]
        self.FieldsDict = {fld.FieldName: fld for fld in flds}
        for i in range(len(self.Fields)):
            self.Fields[i]._index = i

    def __len__(self):
        return len(self.DataRows)

    # def setMainSubMode(mode: bool):
    #     self.__self.__isMain = mode

    def getOnlyData(self, index: [list, tuple, QModelIndex]):
        """getOnlyData(index: [list, tuple, QModelIndex])
        根据指定的数据位置返回数据的值"""
        r, c = JPQueryFieldInfo.getRC(index)
        return self.DataRows[r].Data(c)

    def getDispText(self, index: [list, tuple, QModelIndex]):
        """getDispText(index: [list, tuple, QModelIndex])
        根据指定的数据位置返回数据的显示文本"""
        r, c = JPQueryFieldInfo.getRC(index)
        v = self.DataRows[r].Data(c)
        rs = self.Fields[c].RowSource
        if not v:
            return ''
        if rs:
            txts = [item[1] for item in rs if item[0] == v]
            if txts:
                return txts[0]
        else:
            return JPGetDisplayText(v, FieldInfo=self.Fields[c])

    def getRowData(self, row_num) -> list:
        """根据指定的行号返回一个列表,仅仅包含数据"""
        return self.DataRows[row_num].Datas

    def getFieldsInfo(self):
        return self.Fields

    def getRowFieldsInfoAndData(self, row_num: int) -> list:
        """getRowFieldsInfoAndData(row_num: int)
        根据指定的行号返回一个列表，包含所有FieldInfo对象，且有Value属性"""
        flds = deepcopy(self.Fields)
        data = self.DataRows[row_num]
        for i, fld in flds:
            fld.Value = data[i]
        return flds

    def getRowFieldsInfoDict(self, row_num: int) -> dict:
        """getRowValueDict(row_num: int)
        根据指定的行号返回一个字典，键是字段名，值为FieldInfo对象，且有Value属性"""
        flds = deepcopy(self.Fields)
        data = self.DataRows[row_num].Datas
        r = {}
        for i, item in enumerate(data):
            flds[i].Value = item
            r[flds[i].FieldName] = flds[i]
        return r

    def getRowValueDict(self, row_num: int) -> dict:
        """getRowValueDict(row_num: int)
        根据指定的行号返回一个字典，键是字段名，值为数据"""
        data = self.DataRows[row_num].Datas
        r = {}
        for i, item in enumerate(data):
            r[self.Fields[i].FieldName] = item
        return r

    def getFieldsInfoDict(self) -> dict:
        """返回一个FieldsInfo对象的字典，键是字段名"""
        return self.FieldsDict

    def getFieldInfoAndData(self, index: [list, tuple,
                                          QModelIndex]) -> JPFieldInfo:
        """
         getFieldInfoAndData(index: [list, tuple,QModelIndex])-> JPFieldInfo
        根据行列返回一个包含Value属性的JPFieldInfo对象
        
        """
        r, c = self.getRC(index)
        fld = deepcopy(self.Fields[c])
        fld.value = self.DataRows[r][0][c]

    def setFieldsRowSource(self, key, data: list, binding_column: int = 1):
        '''setFieldsRowSource(key, data:list)\n
            key可以是序号或字段名
        '''
        if isinstance(key, str):
            self.FieldsDict[key].RowSource = data
            self.FieldsDict[key].BindingColumn = binding_column
        if isinstance(key, int):
            self.Fields[key].RowSource = data
            self.Fields[key].BindingColumn = binding_column


class JPTabelFieldInfo(JPQueryFieldInfo):
    def __init__(self, sql: str, noData: bool = False):
        '''根据一个Sql或表名返回一个JPTabelFieldInfo对象\n
        JPTabelFieldInfo(sql:str, noData:bool=False)
        '''
        db = JPDb()
        self.PrimarykeyFieldName = None
        self.PrimarykeyFieldIndex = None
        self.TableName = None
        self.DeleteRows = []

        sql = re.sub(r'^\s', '', re.sub(r'\s+', ' ', re.sub(r'\n', '', sql)))
        sel_p = r"^SELECT\s+.*from\s(\S+)[$|\s].*"
        mt = re.match(sel_p, sql, flags=(re.I | re.M))
        self.TableName = mt.groups()[0] if mt else sql
        s_filter = db.getOnlyStrcFilter()
        if noData:
            # 找出不包含条件的SQL语句
            p_s = r"^(SELECT\s+.*from\s(\S+)[$|\s](as\s\S+)*)"
            mt1 = re.match(p_s, sql, flags=(re.I | re.M))
            sql = mt1.groups(
            )[0] + " " + s_filter if mt else 'Select * from {} {}'.format(
                self.TableName, s_filter) if mt else sql
        else:
            sql = sql if mt else 'Select * from {} {}'.format(sql, s_filter)
        super().__init__(sql)

        # 检查查询结果中是否包含主键,
        for i, fld in enumerate(self.Fields):
            if fld.IsPrimarykey is True:
                self.PrimarykeyFieldName = fld.FieldName
                self.PrimarykeyFieldIndex = i
        if self.PrimarykeyFieldIndex is None:
            raise ValueError('查询语句:\n"{}"中未包含主键字段！'.format(sql))
        # 检查主键字段是不是自增
        #pk_fld = self.getFieldsInfoDict()

    def setData(self, index: [list, tuple, QModelIndex], value=None):
        r, c = super().getRC(index)
        fld = self.Fields[c]
        conDict = fld.getConvertersDict()
        conver = conDict[fld.TypeCode]
        self.DataRows[r].setData(c, conver(value))

    def addRow(self):
        '''增加一行数据，全为None'''
        newRow = JPTabelRowData(len(self.Fields))
        newRow._state = JPTabelRowData.New_None
        self.DataRows.append(newRow)

    def deleteRow(self, row_num: int):
        self.DeleteRows.append(self.DataRows[row_num])
        del self.DataRows[row_num]
