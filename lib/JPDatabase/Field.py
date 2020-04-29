from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from pymysql.constants import FIELD_TYPE
from PyQt5.QtCore import Qt, QDate

from lib.JPFunction import JPDateConver, JPGetDisplayText
from abc import abstractmethod
from decimal import Decimal
from datetime import date as datetime_date


class JPFieldType(object):
    Int = 1
    Float = 2
    String = 3
    Date = 4
    Boolean = 5
    Other = 0


class JPFieldInfo(JPFieldType):
    result_DataAlignment = {
        JPFieldType.Int: (Qt.AlignRight | Qt.AlignVCenter),
        JPFieldType.Float: (Qt.AlignRight | Qt.AlignVCenter),
        JPFieldType.String: (Qt.AlignLeft | Qt.AlignVCenter),
        JPFieldType.Date: (Qt.AlignCenter),
        JPFieldType.Boolean: (Qt.AlignCenter),
        JPFieldType.Other: (Qt.AlignRight | Qt.AlignVCenter)
    }

    def __init__(self):
        self._index = None
        self.FieldName = None
        self.Title = None
        self.TypeCode = None
        self.Scale = None
        self.Length = None
        self.NotNull = None
        self.IsPrimarykey = None
        self.NoDefaultValue = None
        self.Auto_Increment = None
        self.DefaultValue = None
        self.Comment = None
        self.RowSource = None
        self.BindingColumn = None
        self.Formula = None

    @property
    def Alignment(self):
        return self.result_DataAlignment[self.TypeCode]

    @abstractmethod
    def INIT(self):
        return self


class JPMySQLFieldInfo(JPFieldInfo):
    NOT_NULL_FLAG = 1
    PRI_KEY_FLAG = 2
    UNIQUE_KEY_FLAG = 4  #唯一约束
    MULTIPLE_KEY_FLAG = 8  #复合主键
    BLOB_FLAG = 16
    UNSIGNED_FLAG = 32  # 无符号
    ZEROFILL_FLAG = 64  # 前导零
    BINARY_FLAG = 128
    ENUM_FLAG = 256
    AUTO_INCREMENT_FLAG = 512  #自动编号
    TIMESTAMP_FLAG = 1024
    NO_DEFAULT_VALUE_FLAG = 4096
    PART_KEY_FLAG = 16384
    tp = {
        FIELD_TYPE.TINY: JPFieldInfo.Int,
        FIELD_TYPE.SHORT: JPFieldInfo.Int,
        FIELD_TYPE.LONG: JPFieldInfo.Int,
        FIELD_TYPE.LONGLONG: JPFieldInfo.Int,
        FIELD_TYPE.INT24: JPFieldInfo.Int,
        FIELD_TYPE.YEAR: JPFieldInfo.Int,
        FIELD_TYPE.DECIMAL: JPFieldInfo.Float,
        FIELD_TYPE.FLOAT: JPFieldInfo.Float,
        FIELD_TYPE.DOUBLE: JPFieldInfo.Float,
        FIELD_TYPE.NEWDECIMAL: JPFieldInfo.Float,
        FIELD_TYPE.VARCHAR: JPFieldInfo.String,
        FIELD_TYPE.JSON: JPFieldInfo.String,
        FIELD_TYPE.VAR_STRING: JPFieldInfo.String,
        FIELD_TYPE.STRING: JPFieldInfo.String,
        FIELD_TYPE.DATE: JPFieldInfo.Date,
        FIELD_TYPE.DATETIME: JPFieldInfo.Date,
        FIELD_TYPE.NEWDATE: JPFieldInfo.Date,
        FIELD_TYPE.TIMESTAMP: JPFieldInfo.Date,
        FIELD_TYPE.BIT: JPFieldInfo.Boolean
    }

    SqlValueCreater = {
        JPFieldInfo.Int:
        lambda x: "'{}'".format(x),
        JPFieldInfo.Float:
        lambda x: "'{}'".format(x),
        JPFieldInfo.String:
        lambda x: "'{}'".format(x),
        JPFieldInfo.Date:
        lambda x: "'{}'".format(JPDateConver(x, str)),
        JPFieldInfo.Boolean:
        lambda x: "'{}'".format(ord(x) if isinstance(x, bytes) else x),
        JPFieldInfo.Other:
        lambda x: "'{}'".format(x)
    }

    @staticmethod
    def getConvertersDict() -> dict:
        def v_float(x):
            if isinstance(x, Decimal):
                return float(x.to_eng_string())
            if isinstance(x, (float, int, str)):
                return float(x)

        def v_date(x):
            if isinstance(x, QDate):
                return x
            if isinstance(x, datetime_date):
                return QDate(x.year, x.month, x.day)

        def v_bool(x):
            if isinstance(x, bool):
                return 1 if x else 0
            if isinstance(x, bytes):
                return ord(x)

        def v_int(x):
            if isinstance(x, str):
                if len(x) > 0:
                    return int(x)
            return x

        return {
            JPFieldInfo.Int: v_int,
            JPFieldInfo.Float: v_float,
            JPFieldInfo.String: lambda x: x,
            JPFieldInfo.Date: v_date,
            JPFieldInfo.Boolean: v_bool,
            JPFieldInfo.Other: lambda x: x
        }

    def __init__(self, cursors_field):
        """此类在处理时，应该已经把从表中取得的数据全部转换成了Python内部数据类型"""
        super().__init__()
        f = cursors_field
        fl = JPMySQLFieldInfo
        self.FieldName = f.org_name if f.org_name else f.name
        self.Title = f.name
        self.TypeCode = self.tp.get(f.type_code, 0)
        self.Scale = f.scale
        self.Length = f.length
        self.NotNull = f.flags & fl.NOT_NULL_FLAG != 0
        self.IsPrimarykey = f.flags & fl.PRI_KEY_FLAG != 0
        self.NoDefaultValue = f.flags & fl.NO_DEFAULT_VALUE_FLAG != 0
        self.Auto_Increment = f.flags & fl.AUTO_INCREMENT_FLAG != 0

    def sqlValue(self, value, check_null: bool = False):
        v = value
        if check_null:
            if self.NotNull and v is None:
                t = self.Title if self.Title else self.FieldName
                raise ValueError(
                    "字段[{title}]的值不能为空!\nField[{title}] not be Empty!".format(
                        title=t))
        tp = self.TypeCode
        if v is None:
            return 'Null'
        return self.SqlValueCreater[tp](v)
