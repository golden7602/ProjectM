# -*- coding: utf-8 -*-

import abc
import datetime
import os
import re
import sys
sys.path.append(os.getcwd())

from PyQt5 import QtWidgets as QtWidgets_
from PyQt5.QtCore import QDate, QObject, Qt, pyqtSignal
from PyQt5.QtGui import (QColor, QDoubleValidator, QIntValidator, QPalette,
                         QValidator, QPainter, QColor)
from PyQt5.QtWidgets import QCheckBox as QCheckBox_
from PyQt5.QtWidgets import QComboBox as QComboBox_
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QDateEdit as QDateEdit_
from PyQt5.QtWidgets import QLineEdit as QLineEdit_
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTextEdit as QTextEdit_
from PyQt5.QtWidgets import QWidget as QWidget_
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Field import JPFieldType
from lib.JPDatabase.Query import JPTabelRowData
from lib.JPException import JPExceptionFieldNull
from lib.JPFunction import JPBooleanString, JPDateConver, JPGetDisplayText


def __getattr__(name):
    return QtWidgets_.__dict__[name]


class _JPDoubleValidator(QDoubleValidator):
    def __init__(self, v1, v2, decima=2):
        super().__init__()
        self.decima = decima
        self.setDecimals(decima)
        self.min = v1
        self.max = v2

    # def validate(self, vstr, pos):
    #     if (vstr is None) or (vstr == ''):
    #         return QValidator.Acceptable, vstr, pos
    #     str0 = vstr.replace(',', '')
    #     if str0 == '' or str0=="0":
    #         return QValidator.Intermediate, vstr, pos
    #     if str0 == "-":
    #         if self.min < 0.0:
    #             return QValidator.Intermediate, vstr, pos
    #         if self.min > 0.0:
    #             return QValidator.Invalid, vstr, pos
    #     if re.match(r"^-?[1-9]\d*\.?$", str0, flags=(re.I)):
    #         return QValidator.Intermediate, vstr, pos
    #     else:
    #         if re.match(r"^-?[1-9]\d*\.\d{1," + str(self.decima) + r"}$",
    #                     str0,
    #                     flags=(re.I)):
    #             return QValidator.Acceptable, vstr, pos
    #     return QValidator.Invalid, vstr, pos


class _JPIntValidator(QValidator):
    def __init__(self, v1, v2):
        super().__init__()
        self.min = v1
        self.max = v2

    def validate(self, vstr, pos):
        if (vstr is None) or (vstr == ''):
            return QValidator.Acceptable, vstr, pos
        str0 = vstr.replace(',', '')
        if self.min < 0 or self.max < 0:
            if str0 == '-':
                return QValidator.Acceptable, str0, pos
        mt = re.match(r"^-?[1-9]\d*$", str0, flags=(re.I))
        if mt:
            if self.min <= int(str0) <= self.max:
                return QValidator.Acceptable, str0, pos
            elif self.min > int(str0):
                return QValidator.Intermediate, str0, pos
        return QValidator.Invalid, str0, pos


class _JPWidgetBase(QObject):
    def __init__(self, *args):
        super().__init__(*args)
        self.__FieldInfo: JPFieldType = None
        self.MainModel = None
        self.RowsData = None
        self.Null_prompt_bac_color = QColor(255, 192, 203)
        #self.setAutoFillBackground(True)
    @staticmethod
    def getRGBString(color):
        r = color.red()
        g = color.green()
        b = color.blue()
        return f'rgb({r}, {g}, {b})'

    @property
    def _clearStyleSheetText(self):
        txt = "font-family: {font_name};font-size:{px}px;".format(
            font_name=self.fontInfo().family(), px=self.fontInfo().pixelSize())
        return txt

    def setRedStyleSheet(self):
        rgb_s = _JPWidgetBase.getRGBString(self.Null_prompt_bac_color)
        bk = "{background: " + rgb_s + "}"
        s = f'''
        QComboBox{bk}
        QLineEdit{bk}
        QDateEdit{bk}
        QTextEdit{bk}
        QCheckBox{bk}
        '''
        self.setStyleSheet(s)

    def clearStyleSheet(self):
        self.setStyleSheet(self._clearStyleSheetText)

    def _onValueChange(self, value):
        self.RowsData.setData(self.FieldInfo._index, self.Value())
        if self.MainModel:
            self.MainModel._emitDataChange(self, value)

    def setMainModel(self, QWidget: QWidget_):
        self.MainModel = QWidget
        if self.MainModel.isReadOnlyMode:
            self.setFocusPolicy(Qt.NoFocus)

    def setRowsData(self, rd: JPTabelRowData):
        self.RowsData = rd

    @property
    def FieldInfo(self):
        errStr = "窗体字段【{}】的FieldInfo属性为None，可能是窗体SQl查询语句中没有包含此字段！"
        if self.__FieldInfo is None:
            raise AttributeError(errStr.format(self.objectName()))
        return self.__FieldInfo

    @FieldInfo.setter
    def FieldInfo(self, fld):
        self.__FieldInfo = fld

    def getNullValue(self):
        # 检查空值.更改颜色
        fld = self.FieldInfo
        if fld.IsPrimarykey or fld.Auto_Increment:
            return
        else:
            if fld.NotNull is False:
                return 'Null'
            else:
                t = fld.Title if fld.Title else fld.FieldName
                self.setRedStyleSheet()
                raise JPExceptionFieldNull(t)

    @abc.abstractmethod
    def getSqlValue(self):
        """返回字段值，可直接用于SQL语句中"""
        pass

    def setFieldInfo(self, fld: JPFieldType = None, raiseEvent=True):
        self._setFieldInfo(fld, raiseEvent)
        # 设置控件只读状态
        self.setEnabled(not self.MainModel.isReadOnlyMode)

    @abc.abstractmethod
    def _setFieldInfo(self, fld: JPFieldType = None, raiseEvent=True):
        pass

    @abc.abstractmethod
    def Value(self):
        pass

    def refreshValueNotRaiseEvent(self, *value):
        if value:
            self.FieldInfo.Value = value

    def setReadOnly(self, state=True):
        if isinstance(self, (QLineEdit_, QTextEdit_, QDateEdit_)):
            self.setReadOnly(state)
        elif isinstance(self, QComboBox_):
            self.setEnabled(not state)
        elif isinstance(self, QCheckBox_):
            self.setCheckable(not state)

    def isNumeric(self):
        lst = (JPFieldType.Int, JPFieldType.Float)
        return self.__FieldInfo.TypeCode in lst


class QLineEdit(QLineEdit_, _JPWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.passWordConver = None
        self.Validator = None
        self.textChanged[str].connect(self.__onlyRefreshDisplayText)
        self.setAttribute(Qt.WA_InputMethodEnabled, False)

    def getSqlValue(self) -> str:
        t = self.text()
        if self.passWordConver:
            return "'{}'".format(self.passWordConver(t))
        if t is None or len(t) == 0:
            return self.getNullValue()
        self.clearStyleSheet()
        if self.isNumeric():
            return "'{}'".format(t.replace(',', ''))
        if self.FieldInfo.TypeCode == JPFieldType.String:
            return "'{}'".format(t.replace("'", "\\'"))
        return "'{}'".format(t)

    def refreshValueNotRaiseEvent(self, v, changeDisplayText: bool = False):

        try:
            tp = self.FieldInfo.TypeCode
        except AttributeError as e:
            print('【{}】字段FieldInfo属性出错'.format(self.objectName()) + '\n' +
                  str(e))
        else:
            if tp == JPFieldType.Int:
                self.FieldInfo.Value = int(str(v).replace(',', '')) if v else 0
            elif tp == JPFieldType.Float:
                self.FieldInfo.Value = float(str(v).replace(',',
                                                            '')) if v else 0.0
            else:
                self.FieldInfo.Value = v
            if changeDisplayText:
                self.__setDisplayText()

    def refreshValueRaiseEvent(self, v, changeDisplayText: bool = False):
        self.refreshValueNotRaiseEvent(v, changeDisplayText)
        super()._onValueChange(self.FieldInfo.Value)

    def Value(self):
        # 这里是为了处理在主窗体中使用了一些主数据库中没有的字段时
        if self.FieldInfo is None:
            return self.text()
        tp = self.FieldInfo.TypeCode
        v = self.text()
        if tp == JPFieldType.Int:
            return int(v.replace(',', '')) if v else 0
        if tp == JPFieldType.Float:
            return float(v.replace(',', '')) if v else 0.0
        if tp == JPFieldType.String:
            return v if v else ''
        return v

    def _setFieldInfo(self, fld: JPFieldType, raiseEvent=True):
        self.FieldInfo = fld
        st = self.MainModel.isReadOnlyMode
        if not self.MainModel.isNewMode:
            self.__setDisplayText()
        # 设置验证器
        tp = self.FieldInfo.TypeCode
        if tp == JPFieldType.Int:
            self.setIntValidator(0, 999999999999)
        elif tp == JPFieldType.Float:
            self.setDoubleValidator(0.0, 999999999999.99, fld.Scale)
        elif tp == JPFieldType.String:
            self.setMaxLength(fld.Length)

    def keyPressEvent(self, KeyEvent):
        # 限制只能输入数字及小数点,不能输入科学计数法的e
        if self.isNumeric():
            if not KeyEvent.text() in '-.0123456789':
                return
            else:
                QLineEdit_.keyPressEvent(self, KeyEvent)
        else:
            QLineEdit_.keyPressEvent(self, KeyEvent)

    def __setDisplayText(self):
        v = self.FieldInfo.Value
        if v:
            self.setText(JPGetDisplayText(v, FieldInfo=self.FieldInfo))
        else:
            if self.isNumeric():
                self.setText('0')
            else:
                self.setText('')

    def setDoubleValidator(self, v_Min, v_Max, Decimals: int = 2):
        # print(self.objectName(), v_Min, v_Max, Decimals)
        Validator = _JPDoubleValidator(v_Min, v_Max, Decimals)
        Validator.setRange(float(v_Min), float(v_Max))
        Validator.setDecimals(Decimals)
        self.setValidator(Validator)
        self.Validator = Validator

    def setIntValidator(self, v_Min: int, v_Max: int):
        Validator = _JPIntValidator(v_Min, v_Max)
        self.setValidator(Validator)
        self.Validator = Validator

    def __onlyRefreshDisplayText(self, v):
        self.setText(v)

    def isSignalConnected(self, obj, name):
        """判断信号是否连接
        :param obj:        对象
        :param name:       信号名，如 clicked()
        """
        index = obj.metaObject().indexOfMethod(name)
        if index > -1:
            method = obj.metaObject().method(index)
            if method:
                return obj.isSignalConnected(method)
        return False

    def focusInEvent(self, e):
        # 如果此对象没有被赋值字段信息
        try:
            if self.isNumeric():
                t = self.text()
                self.textChanged[str].disconnect(self.__onlyRefreshDisplayText)
                self.setText(t.replace(',', ''))
                self.textChanged[str].connect(self.__onlyRefreshDisplayText)
        except Exception:
            pass
        finally:
            QLineEdit_.focusInEvent(self, e)

    def focusOutEvent(self, e):
        txt = self.text()
        errtxt = '您输入的值小于允许值，已经自动调整为最小合法值。\n'
        errtxt = errtxt + 'The value you entered is less than '
        errtxt = errtxt + 'the allowable value and has been '
        errtxt = errtxt + 'automatically adjusted to the minimum legal value.'
        if txt:
            if self.Validator:
                min = self.Validator.min
                cur = None
                if txt == '-' or txt == '-.':
                    self.refreshValueNotRaiseEvent('', True)
                    return
                if isinstance(min, float):
                    cur = float(txt)
                if isinstance(min, int):
                    cur = int(txt)
                if cur < min:
                    QMessageBox.warning(self.parent(), "提示", errtxt)
                    self.refreshValueNotRaiseEvent(str(min), True)
                else:
                    self.refreshValueNotRaiseEvent(txt, True)
            else:
                self.refreshValueNotRaiseEvent(txt, True)
        else:
            self.refreshValueNotRaiseEvent(txt, True)
        super()._onValueChange(self.FieldInfo.Value)
        QLineEdit_.focusOutEvent(self, e)


class QTextEdit(QTextEdit_, _JPWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.textChanged.connect(self.refreshValueNotRaiseEvent)

    def getSqlValue(self) -> str:
        t = self.toPlainText()
        if t is None or len(t) == 0:
            return self.getNullValue()
        self.clearStyleSheet()
        return "'{}'".format(t.replace("'", "\\'"))

    def _setFieldInfo(self, fld: JPFieldType, raiseEvent=True):
        self.FieldInfo = fld
        self.setPlainText(fld.Value)

    def Value(self):
        return self.FieldInfo.Value

    def refreshValueNotRaiseEvent(self, *args):
        if args:
            self.FieldInfo.Value = args[0]
            if len(args) == 2:
                if args[1]:
                    self.setPlainText(str(args[0]) if args[0] else '')

    def refreshValueRaiseEvent(self, *Value):
        self.refreshValueNotRaiseEvent(Value, True)
        super()._onValueChange(self.FieldInfo.Value)

    def focusOutEvent(self, e):
        super()._onValueChange(self.FieldInfo.Value)
        QTextEdit_.focusOutEvent(self, e)


class QComboBox(QComboBox_, _JPWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.BindingData = []
        self.currentIndexChanged[int].connect(self._onValueChange)
        self.setAttribute(Qt.WA_InputMethodEnabled, False)

    def getSqlValue(self) -> str:
        if self.count() == 0:
            return self.getNullValue()
        if self.currentData():
            tempV = self.BindingData[self.currentIndex()]
            if tempV:
                self.clearStyleSheet()
                return "'{}'".format(tempV)
            else:
                return self.getNullValue()
        else:
            return self.getNullValue()

    def _onValueChange(self, index):
        self.FieldInfo.Value = self.BindingData[index]
        super()._onValueChange(self.FieldInfo.Value)

    def Value(self):
        return self.FieldInfo.Value

    def __setCurrentData(self, value):
        if value is None:
            self.setCurrentIndex(-1)
            return -1
        for i, data in enumerate(self.BindingData):
            if data == value:
                self.FieldInfo.Value = data
                self.setCurrentIndex(i)
                return i

    def refreshValueNotRaiseEvent(self, value):
        self.currentIndexChanged[int].disconnect(self._onValueChange)
        self.__setCurrentData(value)
        self.currentIndexChanged[int].connect(self._onValueChange)

    def refreshValueRaiseEvent(self, value):
        i = self.__setCurrentData(value)
        super()._onValueChange(i)

    @property
    def RowSource(self) -> list:
        return self.FieldInfo.RowSource

    def setEditable(self, state: bool):
        if state:
            super().setEditable(state)
            qcom = QCompleter([str(r[0]) for r in self.FieldInfo.RowSource])
            qcom.setCaseSensitivity(Qt.CaseInsensitive)
            qcom.setCompletionMode(QCompleter.PopupCompletion)
            qcom.setFilterMode(Qt.MatchContains)
            self.setCompleter(qcom)

        else:
            super().setEditable(state)

    def _setFieldInfo(self, fld: JPFieldType, raiseEvent=True):
        self.currentIndexChanged[int].disconnect(self._onValueChange)
        self.FieldInfo = fld
        self.clear()
        self.clearEditText()
        if self.FieldInfo.RowSource:
            for r in self.FieldInfo.RowSource:
                self.addItem(str(r[0]), r)
        c = self.FieldInfo.BindingColumn
        if self.FieldInfo.RowSource is None:
            txt = "窗体字段【{}】没有设置行来源数据,"
            txt = txt + "如果本字段是输入字段，请修改字段控件类型为LineEdit"
            raise AttributeError(txt.format(self.objectName()))
        self.BindingData = [row[c] for row in self.FieldInfo.RowSource]
        # 设置编辑状态
        # self.setEnabled(not self.MainModel.isReadOnlyMode)
        self.__setCurrentData(fld.Value)
        self.currentIndexChanged[int].connect(self._onValueChange)


class QDateEdit(QDateEdit_, _JPWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.__RaiseEvent = False
        self.dateChanged.connect(self._onValueChange)

    def textFromDateTime(self, *args, **kwargs):
        # 当日期值为初始值及Qdate最小值时，显示空值
        v = self.date()
        if self.minimumDate() == v and v == QDate(1752, 9, 14):
            return ''
        else:
            return super().textFromDateTime(*args, **kwargs)

    def getSqlValue(self) -> str:
        v = self.date()
        if self.minimumDate() == v and v == QDate(1752, 9, 14):
            self.FieldInfo.Value = None
            return self.getNullValue()
        else:
            self.clearStyleSheet()
        return "'{}'".format(JPDateConver(self.date(), str))

    def _onValueChange(self, v):
        v = self.date()
        if self.minimumDate() == v and v == QDate(1752, 9, 14):
            return
        self.FieldInfo.Value = JPDateConver(self.date(), datetime.date)
        if self.__RaiseEvent:
            super()._onValueChange(self.FieldInfo.Value)

    def refreshValueNotRaiseEvent(self, value):
        self.__RaiseEvent = False
        value = value if value else self.minimumDate()
        self.FieldInfo.Value = JPDateConver(value, datetime.date)
        self.setDate(JPDateConver(self.FieldInfo.Value, QDate))
        self.__RaiseEvent = True

    def refreshValueRaiseEvent(self, value):
        self.refreshValueNotRaiseEvent(value)
        super()._onValueChange(self.FieldInfo.Value)

    def _setFieldInfo(self, fld: JPFieldType, raiseEvent=True):
        self.FieldInfo = fld
        self.refreshValueNotRaiseEvent(fld.Value)

    def Value(self):
        return JPDateConver(self.date(), datetime.date)

    def mousePressEvent(self, MouseEvent):
        self.setDate(QDate.currentDate())
        super().mousePressEvent(MouseEvent)


class QCheckBox(QCheckBox_, _JPWidgetBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.__RaiseEvent = False
        self.stateChanged[int].connect(self._onValueChange)

    def getSqlValue(self) -> str:
        if self.checkState() is None:
            return self.getNullValue()
        self.clearStyleSheet()
        return '1' if self.checkState() == 2 else '0'

    def _onValueChange(self):
        self.FieldInfo.Value = self.checkState()
        if self.__RaiseEvent:
            super()._onValueChange(self.FieldInfo.Value)

    def refreshValueNotRaiseEvent(self, value):
        self.__RaiseEvent = False
        v = 1 if value else 0
        self.FieldInfo.Value = v
        c = True if value else False
        self.setChecked(c)
        self.__RaiseEvent = True

    def refreshValueRaiseEvent(self, value):
        self.refreshValueNotRaiseEvent(value)
        super()._onValueChange(self.FieldInfo.Value)

    def _setFieldInfo(self, fld: JPFieldType, raiseEvent=True):
        self.FieldInfo = fld
        self.refreshValueNotRaiseEvent(self.FieldInfo.Value)
        self.refreshValueNotRaiseEvent(fld.Value)

    def Value(self):
        return 1 if self.checkState() == Qt.Checked else 0
