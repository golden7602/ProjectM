from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

from Ui.Ui_FormConfig import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QMessageBox, QColorDialog, QFileDialog
from PyQt5.QtGui import QColor
from lib.JPPublc import JPPub
from PyQt5.QtCore import Qt
from lib.JPDatabase.Database import JPDb
from functools import partial


class Form_Config(QDialog):
    @staticmethod
    def getRGBString(color):
        r = color.red()
        g = color.green()
        b = color.blue()
        return f'rgb({r}, {g}, {b})'

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        pub = JPPub()
        super().__init__(parent=pub.MainForm, flags=flags)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        pub.MainForm.addOneButtonIcon(self.ui.colorpicker, 'color_picker.ico')
        pub.MainForm.addOneButtonIcon(self.ui.colorpicker_2,
                                      'color_picker.ico')
        pub.MainForm.addOneButtonIcon(self.ui.taxRegPathSelect,
                                      'folder_explore.ico')
        # 读取信息
        self.configData = pub.getConfigData()

        # 写信息到窗体控件
        self.ui.Note_PrintingOrder.setText(
            self.configData['Note_PrintingOrder'])
        self.ui.Bank_Account.setText(self.configData['Bank_Account'])

        color = self.configData.get('Null_prompt_bac_color', QColor(255, 0, 0))
        c_str = Form_Config.getRGBString(color)
        self.ui.Null_prompt_bac_color.setStyleSheet(
            f"background-color: {c_str}")

        color = self.configData.get('PrintHighlightBackgroundColor',
                                    QColor(194, 194, 194))
        c_str = Form_Config.getRGBString(color)
        self.ui.PrintHighlightBackgroundColor.setStyleSheet(
            f"background-color: {c_str}")

        self.ui.radioButton_AutoShrinkFonts.setChecked(
            self.configData.get("AutoShrinkFonts", False))
        self.ui.radioButton_AutoEllipsis.setChecked(
            self.configData.get("AutoEllipsis", False))
        self.ui.radioButton_AutoRefreshWhenDataChange_Open.setChecked(
            self.configData.get("AutoRefreshWhenDataChange", True))
        self.ui.radioButton_BubbleTipsWhenDataChange_Open.setChecked(
            self.configData.get("BubbleTipsWhenDataChange", True))

        self.ui.radioButton_AutoRefreshWhenDataChange_Close.setChecked(
            not self.ui.radioButton_AutoRefreshWhenDataChange_Open.isChecked())
        self.ui.radioButton_BubbleTipsWhenDataChange_Close.setChecked(
            not self.ui.radioButton_BubbleTipsWhenDataChange_Open.isChecked())

        self.ui.BillCopys_Order.setText(self.configData['BillCopys_Order'])
        self.ui.BillCopys_PrintingOrder.setText(
            self.configData['BillCopys_PrintingOrder'])
        self.ui.BillCopys_OutboundOrder.setText(
            self.configData['BillCopys_OutboundOrder'])
        self.ui.BillCopys_WarehouseRreceipt.setText(
            self.configData['BillCopys_WarehouseRreceipt'])
        self.ui.BillCopys_QuotationOrder.setText(
            self.configData['BillCopys_QuotationOrder'])
        self.ui.BillCopys_QuotationPrintingOrder.setText(
            self.configData['BillCopys_QuotationPrintingOrder'])

        self.ui.TaxRegCerPath.setText(self.configData['TaxRegCerPath'])

        # 事件处理

        self.ui.Note_PrintingOrder.textChanged.connect(self.configChanged)
        self.ui.Bank_Account.textChanged.connect(self.configChanged)
        self.ui.colorpicker.clicked.connect(
            partial(self.backColorSelect, self.ui.Null_prompt_bac_color))
        self.ui.colorpicker_2.clicked.connect(
            partial(self.backColorSelect,
                    self.ui.PrintHighlightBackgroundColor))
        self.ui.radioButton_AutoShrinkFonts.toggled.connect(self.configChanged)
        self.ui.radioButton_AutoEllipsis.toggled.connect(self.configChanged)
        self.ui.radioButton_AutoRefreshWhenDataChange_Open.toggled.connect(
            self.configChanged)
        self.ui.radioButton_AutoRefreshWhenDataChange_Open.toggled.connect(
            self.configChanged)
        self.ui.radioButton_AutoRefreshWhenDataChange_Close.toggled.connect(
            self.configChanged)
        self.ui.radioButton_BubbleTipsWhenDataChange_Open.toggled.connect(
            self.configChanged)
        self.ui.radioButton_BubbleTipsWhenDataChange_Close.toggled.connect(
            self.configChanged)
        self.ui.BillCopys_Order.textChanged.connect(self.configChanged)
        self.ui.BillCopys_PrintingOrder.textChanged.connect(self.configChanged)
        self.ui.BillCopys_OutboundOrder.textChanged.connect(self.configChanged)
        self.ui.BillCopys_WarehouseRreceipt.textChanged.connect(
            self.configChanged)
        self.ui.BillCopys_QuotationOrder.textChanged.connect(
            self.configChanged)
        self.ui.BillCopys_QuotationPrintingOrder.textChanged.connect(
            self.configChanged)

        self.ui.taxRegPathSelect.clicked.connect(
            partial(self.folderSelect, self.ui.TaxRegCerPath))
        self.ui.TaxRegCerPath.textChanged.connect(self.configChanged)

        self.exec_()

    def configChanged(self):
        self.configData[
            'Note_PrintingOrder'] = self.ui.Note_PrintingOrder.toPlainText()
        self.configData['Bank_Account'] = self.ui.Bank_Account.toPlainText()
        self.configData[
            'AutoShrinkFonts'] = self.ui.radioButton_AutoShrinkFonts.isChecked(
            )
        self.configData[
            'AutoEllipsis'] = self.ui.radioButton_AutoEllipsis.isChecked()
        self.configData[
            'AutoRefreshWhenDataChange'] = self.ui.radioButton_AutoRefreshWhenDataChange_Open.isChecked(
            )
        self.configData[
            'BubbleTipsWhenDataChange'] = self.ui.radioButton_BubbleTipsWhenDataChange_Open.isChecked(
            )

        self.configData[
            'BillCopys_Order'] = self.ui.BillCopys_Order.toPlainText()
        self.configData[
            'BillCopys_PrintingOrder'] = self.ui.BillCopys_PrintingOrder.toPlainText(
            )
        self.configData[
            'BillCopys_OutboundOrder'] = self.ui.BillCopys_OutboundOrder.toPlainText(
            )
        self.configData[
            'BillCopys_WarehouseRreceipt'] = self.ui.BillCopys_WarehouseRreceipt.toPlainText(
            )
        self.configData[
            'BillCopys_QuotationOrder'] = self.ui.BillCopys_QuotationOrder.toPlainText(
            )
        self.configData[
            'BillCopys_QuotationPrintingOrder'] = self.ui.BillCopys_QuotationPrintingOrder.toPlainText(
            )
        self.configData['TaxRegCerPath'] = self.ui.TaxRegCerPath.text()

    def backColorSelect(self, obj):
        color = QColorDialog.getColor()
        key = obj.objectName()
        if color:
            c_str = self.getRGBString(color)
            obj.setStyleSheet(f"background-color: {c_str}")
            self.configData[key] = color

    def folderSelect(self, obj):
        path = QFileDialog.getExistingDirectory()
        key = obj.objectName()
        if path:
            obj.setText(path)
            self.configData[key] = path

    def accept(self):
        JPPub().saveConfigData(self.configData)
        JPPub().ConfigData(True)
        QMessageBox.information(self, '提示', '保存数据成功！\nSave datas complete!')
        self.close()
