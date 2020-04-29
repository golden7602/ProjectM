# -*- coding: utf-8 -*-

from PyQt5.QtGui import (QIntValidator, QDoubleValidator, QRegExpValidator,
                         QValidator)
from PyQt5.QtCore import QRegExp


class JPValidator(object):
    def __init__(self):
        pass

    def ValidatorCellPhoneNumber(self) -> QValidator:
        # 设置文本允许出现的字符内容
        reg = QRegExp('[0-9]+$')
        # 自定义文本验证器
        Validator = QRegExpValidator()
        # 设置属性
        Validator.setRegExp(reg)
        return Validator


class JPDoubleValidator(QDoubleValidator):
    def __init__(self, decima=2):
        super().__init__()
        self.setDecimals(decima)

    def validate(self, vstr, pos):
        return super().validate(vstr.replace(',', ''), pos)


class JPIntValidator(QIntValidator):
    def __init__(self):
        super().__init__()

    def validate(self, vstr, pos):
        return super().validate(vstr.replace(',', ''), pos)
