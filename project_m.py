#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import logging.handlers
from lib.JPForms.JPMainApp import JPMianApp
from lib.ProjectMWidgets import (
    Form_Project, Form_Archives, Form_Company, FileToolsImport, FileToolsPDF)


if __name__ == "__main__":
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
    CommandDic = {2: Form_Project,
                  186: Form_Archives,
                  198: Form_Company,
                  206: FileToolsImport,
                  207: FileToolsPDF
                  }
    app = JPMianApp(dicConfig)
    app.setMainFormLogo("gaoke.png")
    app.setAppIcon("invoice.png")
    app.setMainFormTitle("文档管理")
    app.setCommand(CommandDic)
    app.show()
