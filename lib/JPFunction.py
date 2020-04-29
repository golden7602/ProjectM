# -*- coding: utf-8 -*-
import datetime
import hashlib
import time
from decimal import Decimal
from functools import singledispatch
from os import getcwd
from sys import path as jppath
import os
import hashlib
jppath.append(getcwd())

from PyQt5.QtCore import QDate, Qt, QDateTime
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget


def seWindowsIcon(win):
    win.setWindowIcon(QIcon(getcwd() + '\\order_162.ico'))


def md5_passwd(str0, salt='al;dkfjgutriepw,cmvnfjisjmwudnus000999'):
    # satl是盐值，
    str0 = salt + str(str0) + salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(str0.encode())
    res = md.hexdigest()
    return res



def setButtonIcon(btn: QPushButton, filename=None):
    fn = filename if filename else btn.text()
    icon = QIcon(getcwd() + "\\res\\ico\\" + fn)
    btn.setIcon(icon)


def setWidgetIconByName(ctl: QPushButton):
    fn = getcwd() + "\\res\\ico\\" + ctl.objectName() + ".png"
    if isinstance(ctl, QLabel):
        pix = QPixmap(fn)
        ctl.setPixmap(pix)

    if isinstance(ctl, QPushButton):
        icon = QIcon(fn)
        ctl.setIcon(icon)


def findButtonAndSetIcon(Widget: QWidget):
    btns = Widget.findChildren((QPushButton))
    for btn in btns:
        setButtonIcon(btn)


def PrintFunctionRunTime(func):
    """计算函数运行时间的装饰器"""
    def run(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print("函数{0}的运行时间为： {1}".format(func.__name__, time.time() - start))
        return result

    return run


def Singleton(cls, *args, **kw):
    """单实例装饰器"""
    instance = {}

    def _singleton():
        if cls not in instance:
            instance[cls] = cls(*args, **kw)
        return instance[cls]

    return _singleton


@Singleton
class JPBooleanString(object):
    __BoolString = (('Non', 0), ('SIM', 1))

    def getBooleanString(self):
        return self.__BoolString

    def setBooleanString(tup: tuple):
        """设置全局逻辑变量的默认值
        格式如 (('', 0), ('SIM', 1))"""
        self.__BoolString = [tup]


def JPReadDataToWidget(Widget, FieldType, FieldValue):
    if FieldValue is None: return
    if FieldType in (1, 3, 8):  # TinyInt,Int
        Widget.setText(str(FieldValue))
    elif FieldType in (7, 10):  # TS,DATE
        pass
        #item.setText(str(FieldValue))
    elif FieldType == 16:  # Bit
        Widget.setText(str(ord(FieldValue)))
    elif FieldType == 246:  # Decimal
        Widget.setText('{:,.2f}'.format(FieldValue))
    elif FieldType in (253, 254):  # VChar,Char
        Widget.setText(str(FieldValue))
    else:  # other
        Widget.setText(str(FieldValue))


def NV(value, mod):
    if isinstance(mod, str):
        return str(value) if value else ''
    if isinstance(mod, int):
        return int(value) if value else 0
    if isinstance(mod, (float, Decimal)):
        return float(value) if value else 0.0
    return value


def JPReadLineToTableWidgetItem(item, FieldType, FieldValue):
    if FieldValue is None: return
    left = (Qt.AlignLeft | Qt.AlignVCenter)
    center = (Qt.AlignCenter | Qt.AlignVCenter)
    right = (Qt.AlignRight | Qt.AlignVCenter)
    if FieldType in (1, 3, 8):  # TinyInt,Int
        item.setText(str(FieldValue))
        item.setTextAlignment(right)
    elif FieldType in (7, 10):  # TS,DATE
        item.setText(str(FieldValue))
        item.setTextAlignment(center)
    elif FieldType == 16:  # Bit
        item.setText(str(ord(FieldValue)))
        item.setTextAlignment(center)
    elif FieldType == 246:  # Decimal
        item.setText('{:,.2f}'.format(FieldValue))
        item.setTextAlignment(right)
    elif FieldType in (253, 254):  # VChar,Char
        item.setText(str(FieldValue))
        item.setTextAlignment(left)
    else:  # other
        item.setText(str(FieldValue))
        item.setTextAlignment(left)


def JPRound(number, power=0):
    """
    实现精确四舍五入，包含正、负小数多种场景
    :param number: 需要四舍五入的小数
    :param power: 四舍五入位数，支持0-∞
    :return: 返回四舍五入后的结果
    """
    if number is None:
        return
    digit = 10**power
    num2 = float(int(number * digit))
    # 处理正数，power不为0的情况
    if number >= 0 and power != 0:
        tag = number * digit - num2 + 1 / (digit * 10)
        if tag >= 0.5:
            return (num2 + 1) / digit
        else:
            return num2 / digit
    # 处理正数，power为0取整的情况
    elif number >= 0 and power == 0:
        tag = number * digit - int(number)
        if tag >= 0.5:
            return (num2 + 1) / digit
        else:
            return num2 / digit
    # 处理负数，power为0取整的情况
    elif power == 0 and number < 0:
        tag = number * digit - int(number)
        if tag <= -0.5:
            return (num2 - 1) / digit
        else:
            return num2 / digit
    # 处理负数，power不为0的情况
    else:
        tag = number * digit - num2 - 1 / (digit * 10)
        if tag <= -0.5:
            return (num2 - 1) / digit
        else:
            return num2 / digit


###################################################################
@singledispatch
def JPGetDisplayText(value, *args, **kwargs) -> str:
    '''返回参数的显示用字符形式
    '''
    if value:
        return
    else:
        return ''


@JPGetDisplayText.register(str)
def _(value, *args, **kwargs):
    return value


@JPGetDisplayText.register(QDate)
def _(value, *args, **kwargs):
    return value.toString("yyyy-MM-dd")


@JPGetDisplayText.register(datetime.date)
def _(value, *args, **kwargs):
    return value.strftime('%Y-%m-%d')


@JPGetDisplayText.register(int)
def _(value, *args, **kwargs):
    if value == 0:
        return ''
    return '{:,}'.format(value)


@JPGetDisplayText.register(float)
def _(value, *args, **kwargs):
    fld = kwargs.get("FieldInfo", False)
    Scale = str(fld.Scale) if fld else '2'
    formatString = "{:,." + Scale + "f}"
    return formatString.format(value)


@JPGetDisplayText.register(Decimal)
def _(value, *args, **kwargs):
    if value == 0:
        return ''
    v = float(str(value))
    fld = kwargs.get("FieldInfo", False)
    Scale = str(fld.Scale) if fld else '2'
    formatString = "{:,." + Scale + "f}"
    return formatString.format(v)


@JPGetDisplayText.register(bytes)
def _(value, *args, **kwargs):
    tup = JPBooleanString().getBooleanString()
    i = ord(value)
    return tup[i]


###################日期转换器###################################################
@singledispatch
def JPDateConver(value, vCls=str):
    '''JPDateConver(value, vCls)\n
    日期转换:value类型可为str、datetime.date、datetime.datatime或QDate\n
    vCls指定输出格式，为一类名可以是datetime.date、QDate或str
    '''
    raise TypeError("JPDateConver函数参数类型错误！")


@JPDateConver.register(str)
def _(value, vCls=str):
    cur_date = QDate.fromString(value, "yyyy-MM-dd")
    if vCls is str:
        return value
    if vCls is QDate:
        return cur_date
    if vCls is datetime.date:
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    raise TypeError("JPDateConver函数vCls参数类型错误！")


@JPDateConver.register(QDate)
def _(value, vCls=str):
    if vCls is str:
        return value.toString("yyyy-MM-dd")
    if vCls is QDate:
        return value
    if vCls is datetime.date:
        return datetime.datetime(value.year(), value.month(),
                                 value.day()).date()
    raise TypeError("JPDateConver函数vCls参数类型错误！")


@JPDateConver.register(datetime.date)
def _(value, vCls=str):
    cur_date = QDate(value.year, value.month, value.day)
    if vCls is str:
        return cur_date.toString("yyyy-MM-dd")
    if vCls is QDate:
        return cur_date
    if vCls is datetime.date:
        return value
    raise TypeError("JPDateConver函数vCls参数类型错误！")


@JPDateConver.register(datetime.datetime)
def _(value, vCls=str):
    cur_date = QDateTime(value.year, value.month, value.day, value.hour,
                         value.minute, value.second)
    if vCls is str:
        return cur_date.toString("yyyy-MM-dd HH:mm:ss")
    if vCls is QDate:
        return QDate(cur_date)
    if vCls is datetime.date:
        return datetime.date(cur_date.year(), cur_date.month(),
                             cur_date.day()).date()
    if vCls is datetime.datetime:
        return value
    raise TypeError("JPDateConver函数vCls参数类型错误！")


def readQss(style):  # Use: win.setStyleSheet(readQss(qssStyle))
    with open(style, 'r') as f:
        return f.read()



# 生成文件哈希值，用于文件名
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myHash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myHash.update(b)
    f.close()
    return myHash.hexdigest()