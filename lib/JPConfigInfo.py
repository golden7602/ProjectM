# -*- coding: utf-8 -*-
from lib.JPFunction import Singleton
from PyQt5.QtWidgets import QMessageBox
from functools import wraps
from configparser import ConfigParser
import os
import sys


@Singleton
class ConfigInfo(object):
    '''配置信息类，自动从配置文件加载信息，可以用本类的"实例名.节.属性"的方式使用'''

    def __init__(self, defaultdict: dict = {}):

        class item(object):
            '''内部类'''

            def __init__(self):
                super().__init__()

            def __getattr__(self, name):
                raise KeyError("属性'{}'不存在，可能是ini文件中没有设置该值!".format(name))
        self.defaultdict = defaultdict
        notFind = '当前文件夹下没有找到"Config.ini"文件！\n已经默认生成了一个，请修改相关参数\n'
        notFind = notFind + '"Config.ini" file was not found in the current folder!'
        self.__inipath = os.path.join(
            os.path.abspath(os.getcwd()), 'config.ini')
        if os.path.exists(self.__inipath) is False:
            QMessageBox.warning(None, '错误', notFind, QMessageBox.Yes,
                                QMessageBox.Yes)
            self._createIniFile()
            sys.exit()
        config = ConfigParser()
        config.read(self.__inipath, encoding="utf-8")
        for sectionName, itemDict in config._sections.items():
            self.__dict__[sectionName] = item()
            temp = self.__dict__[sectionName]
            for itemName, itemValue in itemDict.items():
                temp.__dict__[itemName] = itemValue

    def _createIniFile(self):
        config = ConfigParser()
        for sectionName, itemDict in self.defaultdict.items():
            config[sectionName] = itemDict
        with open(self.__inipath, 'w') as configfile:
            config.write(configfile)

    def __getattr__(self, name):
        raise KeyError("节'{}'不存在，可能是ini文件中没有设置该节!".format(name))



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from sys import argv
    a = QApplication(argv)
    dicConfig = {
        'database': {
            'host': '127.0.0.1',
            'user': 'username',
            'password': 'password',
            'database': 'database',
            'port': '3306'},
        'path': {
            'archives_path': '//192.168.1.20/jhglb/archives'},
        'debug': {
            'level': '50',
            'logfile': 'project.log'},
        'viewpdf': {
            'maxpages': '50',
            'pagesize': '105, 139'}
    }
    cfg = ConfigInfo(dicConfig)
    print(cfg.database.aaa)
    # kw = dict(config._sections["path"])
    # self.tax_reg_path = kw["tax_reg"]
