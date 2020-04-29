# -*- coding: utf-8 -*-
from configparser import ConfigParser
from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())
from PyQt5.QtWidgets import QMessageBox
from lib.JPFunction import Singleton


@Singleton
class ConfigInfo():
    def __init__(self):
        notFind = '当前文件夹下没有找到"Config.ini"文件！\n'
        notFind = notFind + '"Config.ini" file was not found in the current folder!'
        if ospath.exists(getcwd() + '\\config.ini') is False:
            QMessageBox.warning(None, '错误', notFind, QMessageBox.Yes,
                                QMessageBox.Yes)
            exit()
        config = ConfigParser()
        config.read("config.ini", encoding="utf-8")

        kw = dict(config._sections["database"])
        self.host = kw["host"]
        self.user = kw["user"]
        self.password = kw["password"]
        self.database = kw["database"]
        self.port = int(kw['port'])

        # kw = dict(config._sections["path"])
        # self.tax_reg_path = kw["tax_reg"]
