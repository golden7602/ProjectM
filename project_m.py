#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import logging.handlers
from lib.JPForms.JPMainApp import JPMianApp
from lib.ProjectMWidgets.Project import Form_Project
from lib.ProjectMWidgets.Archives import Form_Archives
from lib.ProjectMWidgets.Company import Form_Company
from lib.ProjectMWidgets.ToolsImport import FileToolsImport
from lib.ProjectMWidgets.ToolsPDF import FileToolsPDF
# from guppy import hpy
# hxx = hpy()
# heap = hxx.heap()
# byrcs = hxx.heap().byrcs

if __name__ == "__main__":
    app = JPMianApp()
    app.setMainFormLogo("gaoke.png")
    app.setAppIcon("invoice.png")
    app.setMainFormTitle("文档管理")
    dic = {2: Form_Project,
           186: Form_Archives,
           198: Form_Company,
           206: FileToolsImport,
           207: FileToolsPDF}
    app.setCommand(dic)
#     print(heap)
    app.show()
