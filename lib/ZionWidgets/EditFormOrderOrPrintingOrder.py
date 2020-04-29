# -*- coding: utf-8 -*-
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from Ui.Ui_FormPrintingOrder_Template import Ui_Form as FormPrintingOrder
from Ui.Ui_FormOrder_Template import Ui_Form as FormOrder
from lib.JPPublc import JPPub


def _setEditFormButtonsIcon(ui):
    pub = JPPub()
    fun = pub.MainForm.addOneButtonIcon
    fun(ui.butSave, "save.png")
    fun(ui.butPrint, "print.png")
    fun(ui.butPDF, "pdf.png")


class JPFormOrder(FormOrder):
    def setupUi(self, *args, **kwargs):
        super().setupUi(*args, **kwargs)
        _setEditFormButtonsIcon(self)




class JPFormPrintingOrder(FormPrintingOrder):
    def setupUi(self, *args, **kwargs):
        super().setupUi(*args, **kwargs)
        _setEditFormButtonsIcon(self)

