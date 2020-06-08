from PyQt5.QtCore import QModelIndex
from abc import abstractmethod, ABC
from decimal import Decimal
from datetime import date as datetime_date
import re
# 字段基类


class JPField(ABC):
    def __init__(self):
        """代表一个表中字段的对象"""
        super().__init__()
        self.name = None
        self.comment = None
        self.typeCode = None
        self.scale = None
        self.length = None
        self.notNull = None
        self.isPrimarykey = None
        self.noDefaultValue = None
        self.auto_Increment = None
        self.defaultValue = None
        self.rowSource = None
        self.bindingColumn = 0
        self.formula = None

    def title(self) -> str:
        """返回字段标题：优先返回comment属性的值，如果没有则返回字段名
        """
        if not self.comment and not self.comment:
            raise AttributeError
        else:
            return self.comment if self.comment else self.name

    @property
    def typeName(self) -> str:
        pass

    @abstractmethod
    def displayText(self, any) -> str:
        """返回字段在用户界面上应该显示的字符串"""
        pass

    @abstractmethod
    def Alignment(self):
        """返回字段在用户界面上对齐方式"""
        pass

    @abstractmethod
    def sqlValue(self, value):
        """返回字段的SQL值"""
        pass


class JPFields(object):
    def __init__(self):
        """一个字段集合对象，可通过实例函数方式来获取成员
        例如：a=Fields()
            a(字段名或字段顺序号)可返回一个Field对象
        """
        super().__init__()
        self.__fields = {}

    def __call__(self, fieldName_or_fieldIndex: [str, int]) -> JPField:
        """返回一个JPField对象"""
        # 把类的实例变成一个可执行对象
        pass

    def add(self, jpfield: JPField):
        """增加一个JPField字段对象到集合中"""
        key = (len(self.__fields), jpfield.name)
        self.__fields[key] = jpfield

    def count(self):
        return len(self.__fields)


class JPQuery(object):
    def __init__(self, sql: str):
        super().__init__(self)
        self.__fields = None

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, fields: JPFields):
        self.__fields = fields


    def setRowSource(self, key: [str, int], valueList: list, bpipindingColumn: int = 1):
        """设置一个字段的行来源，用于comboBox显示列表及列表窗体中更换显示值"""
        fld = self.__fields(key)
        fld.rowSource = valueList
        fld.bindingColumn = bindingColumn

    def data(index: QModelIndex,)
