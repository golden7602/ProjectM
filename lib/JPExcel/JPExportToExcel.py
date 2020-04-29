# -*- coding: utf-8 -*-

import time
from os import getcwd
from sys import path as jppath
jppath.append(getcwd())

import xlwt
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from lib.JPDatabase.Query import JPQueryFieldInfo
from lib.JPFunction import JPGetDisplayText
from lib.JPDatabase.Field import JPFieldType


class xls_alignment():
    VERT_TOP = 0x00  #上端对齐
    VERT_CENTER = 0x01  #居中对齐（垂直方向上）
    VERT_BOTTOM = 0x02  #低端对齐
    HORZ_LEFT = 0x01  #左端对齐
    HORZ_CENTER = 0x02  #居中对齐（水平方向上）
    HORZ_RIGHT = 0x03  #右端对齐


class clsExportToExcelFromTableWidget(object):
    def __init__(self, tableWidget, MainForm):
        self.tableWidget = tableWidget
        self.MainForm = MainForm

    def run(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(
            self.MainForm,
            "Export To Excel File Name",
            getcwd(),  # 起始路径
            "Excel Files (*.xls)")
        if not fileName_choose:
            return
        tab = self.tableWidget
        book = xlwt.Workbook(encoding='utf-8')  # 新建一个excel
        sheet = book.add_sheet('newsheet')  # 添加一个sheet页
        borders = xlwt.Borders()  # Create Borders
        borders.left = xlwt.Borders.THIN
        # DASHED虚线 NO_LINE没有 THIN实线
        # May be: NO_LINE, THIN, MEDIUM, DASHED,
        # DOTTED, THICK, DOUBLE, HAIR,
        # MEDIUM_DASHED, THIN_DASH_DOTTED,
        # MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED,
        # MEDIUM_DASH_DOT_DOTTED,
        # SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        style = xlwt.XFStyle()  # Create Style
        style.borders = borders  # Add Borders to Style

        pattern = xlwt.Pattern()  # Create the Pattern
        # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green,
        # 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon,
        # 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow ,
        # almost brown), 20 = Dark Magenta, 21 = Teal,
        # 22 = Light Gray, 23 = Dark Gray, the list goes on...
        pattern.pattern_fore_colour = 22
        style.pattern = pattern  # Add Pattern to Style

        for i in range(0, tab.columnCount()):
            sheet.write(0, i, tab.horizontalHeaderItem(i).text(), style)
        self.MainForm.ProgressBar.show()
        self.MainForm.Label.setText('Exporting')
        self.MainForm.ProgressBar.setRange(0, tab.rowCount())

        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 1
        style1 = xlwt.XFStyle()
        style1.borders = borders
        style1.pattern = pattern1

        for i in range(0, tab.rowCount()):
            for j in range(0, tab.columnCount()):
                self.MainForm.ProgressBar.setValue(i)
                sheet.write(i + 1, j, tab.item(i, j).text(), style1)
        self.MainForm.Label.setText('')
        self.MainForm.ProgressBar.hide()
        book.save(fileName_choose)


class JPExpExcelFromTabelFieldInfo(object):
    def __init__(self, QueryFieldInfo: JPQueryFieldInfo, MainForm):
        """"""
        self.QueryFieldInfo = QueryFieldInfo
        self.MainForm = MainForm
        self.linkMainTableFieldIndex = 0
        self.linkSubTableFieldIndex = 0
        self.SubQueryFieldInfo = None

    def setSubQueryFieldInfo(self,
                             SubQueryFieldInfo: JPQueryFieldInfo,
                             linkMainTableFieldIndex: int = 0,
                             linkSubTableFieldIndex: int = 0):
        self.linkMainTableFieldIndex = linkMainTableFieldIndex
        self.linkSubTableFieldIndex = linkMainTableFieldIndex
        self.SubQueryFieldInfo = SubQueryFieldInfo

    def run(self):
        fileName_choose, filetype = QFileDialog.getSaveFileName(
            self.MainForm,
            "Export To Excel File Name",
            getcwd(),  # 起始路径
            "Excel Files (*.xls)")
        if not fileName_choose:
            return
        book = xlwt.Workbook(encoding='utf-8')  # 新建一个excel
        sheet = book.add_sheet('newsheet')  # 添加一个sheet页
        borders = xlwt.Borders()  # Create Borders
        borders.left = xlwt.Borders.THIN
        # DASHED虚线 NO_LINE没有 THIN实线
        # May be: NO_LINE, THIN, MEDIUM, DASHED,
        # DOTTED, THICK, DOUBLE, HAIR,
        # MEDIUM_DASHED, THIN_DASH_DOTTED,
        # MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED,
        # MEDIUM_DASH_DOT_DOTTED,
        # SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.

        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        style = xlwt.XFStyle()  # Create Style
        style.borders = borders  # Add Borders to Style

        pattern = xlwt.Pattern()  # Create the Pattern
        # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern = xlwt.Pattern.NO_PATTERN
        # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green,
        # 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon,
        # 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow ,
        # almost brown), 20 = Dark Magenta, 21 = Teal,
        # 22 = Light Gray, 23 = Dark Gray, the list goes on...
        pattern.pattern_fore_colour = 22
        style.pattern = pattern  # Add Pattern to Style

        # 写入主表标题
        tab = self.QueryFieldInfo
        mian_cols = len(tab.Fields)
        for i in range(mian_cols):
            sheet.write(0, i, tab.Fields[i].Title, style)
        try:
            self.MainForm.ProgressBar.show()
            self.MainForm.Label.setText('Exporting')
            self.MainForm.ProgressBar.setRange(0, len(tab))
        except Exception:
            pass
        # 写入子表标题
        subTab = self.SubQueryFieldInfo
        if subTab:
            for i in range(len(subTab.Fields)):
                if i != self.linkSubTableFieldIndex:
                    sheet.write(0, mian_cols + i, subTab.Fields[i].Title,
                                style)
        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 1
        style1 = xlwt.XFStyle()
        style1.borders = borders
        style1.pattern = pattern1
        al = xlwt.Alignment()
        al.horz = xls_alignment.HORZ_LEFT
        al.vert = xls_alignment.VERT_CENTER
        style1.alignment = al

        styleR = xlwt.XFStyle()
        styleR.borders = borders
        styleR.pattern = pattern1
        aR = xlwt.Alignment()
        aR.horz = xls_alignment.HORZ_RIGHT
        aR.vert = xls_alignment.VERT_CENTER
        styleR.alignment = aR

        # 开始导出数据
        main_row = 1
        for i in range(len(tab)):
            try:
                self.MainForm.ProgressBar.setValue(i)
            except Exception:
                pass
            # 调用函数，尝试导出子表
            sub_rows = self.__expSub(
                sheet, style1, main_row, mian_cols,
                tab.DataRows[i].Datas[self.linkMainTableFieldIndex])
            # 导出主表
            if sub_rows > 0:
                row1 = main_row
                row2 = main_row + sub_rows - 1
                for col_main in range(mian_cols):

                    v = JPGetDisplayText(tab.DataRows[i].Datas[col_main],
                                         FieldInfo=tab.Fields[col_main])


                    #print(row1, row2, col_main, col_main)
                    sheet.write_merge(row1, row2, col_main, col_main, v,
                                      style1)

            else:
                for col_main in range(mian_cols):
                    v = JPGetDisplayText(tab.DataRows[i].Datas[col_main],
                                         FieldInfo=tab.Fields[col_main])
                    #print(main_row, col_main)
                    tp = tab.Fields[col_main].TypeCode
                    styleTemp = styleR if tp in (JPFieldType.Int,
                                                 JPFieldType.Float) else style1
                    sheet.write(main_row, col_main, v, styleTemp)
            main_row = main_row + (sub_rows if sub_rows else 1)
        try:
            self.MainForm.Label.setText('')
            self.MainForm.ProgressBar.hide()
        except Exception:
            pass
        try:
            book.save(fileName_choose)
        except Exception as e:
            errstr = '写入文件出错！\nWrite file error!\n'
            errstr = errstr + Exception.__repr__(e)
            QMessageBox.information(self.MainForm, '提示', errstr)
        QMessageBox.information(self.MainForm, '提示',
                                '导出数据完成！\nExport to excel complete!')

    def __expSub(self, sheet, style, cur_row, maincols, linkData) -> int:
        if self.SubQueryFieldInfo is None:
            return 0
        li = self.linkSubTableFieldIndex
        tab = self.SubQueryFieldInfo
        sub_cols = len(tab.Fields)
        lst = [r.Datas for r in tab.DataRows if r.Datas[li] == linkData]
        for row in lst:
            cur_col = len(self.QueryFieldInfo.Fields) + 1
            for sub_col in range(sub_cols):
                if sub_col != self.linkSubTableFieldIndex:
                    sheet.write(
                        cur_row, cur_col,
                        JPGetDisplayText(row[sub_col],
                                         FieldInfo=tab.Fields[sub_col]), style)
                    cur_col += 1
            cur_row += 1
        return len(lst)


class JPExpExcelFromManyTabelFieldInfo(object):
    """可以导出多个tableinfo"""

    def __init__(self, *args, **kwargs):
        self.tableInfos = args
        self.MainForm = kwargs.get("MainForm", None)
        self.xlsBook = None

    def __ExportOneTableInfo(self, tab, sht_name):
        sheet = self.xlsBook.add_sheet(sht_name)  # 添加一个sheet页
        borders = xlwt.Borders()  # Create Borders
        borders.left = xlwt.Borders.THIN
        # DASHED虚线 NO_LINE没有 THIN实线
        # May be: NO_LINE, THIN, MEDIUM, DASHED,
        # DOTTED, THICK, DOUBLE, HAIR,
        # MEDIUM_DASHED, THIN_DASH_DOTTED,
        # MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED,
        # MEDIUM_DASH_DOT_DOTTED,
        # SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.

        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        style = xlwt.XFStyle()  # Create Style
        style.borders = borders  # Add Borders to Style

        pattern = xlwt.Pattern()  # Create the Pattern
        # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern = xlwt.Pattern.NO_PATTERN
        # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green,
        # 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon,
        # 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow ,
        # almost brown), 20 = Dark Magenta, 21 = Teal,
        # 22 = Light Gray, 23 = Dark Gray, the list goes on...
        pattern.pattern_fore_colour = 22
        style.pattern = pattern  # Add Pattern to Style

        # 写入主表标题
        mian_cols = len(tab.Fields)
        for i in range(mian_cols):
            sheet.write(0, i, tab.Fields[i].Title, style)
        try:
            self.MainForm.ProgressBar.show()
            self.MainForm.Label.setText('Exporting')
            self.MainForm.ProgressBar.setRange(0, len(tab))
        except Exception:
            pass
        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 1
        style1 = xlwt.XFStyle()
        style1.borders = borders
        style1.pattern = pattern1
        al = xlwt.Alignment()
        al.horz = xls_alignment.HORZ_LEFT
        al.vert = xls_alignment.VERT_CENTER
        style1.alignment = al

        styleR = xlwt.XFStyle()
        styleR.borders = borders
        styleR.pattern = pattern1
        aR = xlwt.Alignment()
        aR.horz = xls_alignment.HORZ_RIGHT
        aR.vert = xls_alignment.VERT_CENTER
        styleR.alignment = aR

        # 开始导出数据
        main_row = 1
        for i in range(len(tab)):
            try:
                self.MainForm.ProgressBar.setValue(i)
            except Exception:
                pass
            for col_main in range(mian_cols):
                v = JPGetDisplayText(tab.DataRows[i].Datas[col_main],
                                        FieldInfo=tab.Fields[col_main])
                #print(main_row, col_main)
                tp = tab.Fields[col_main].TypeCode
                styleTemp = styleR if tp in (JPFieldType.Int,
                                                JPFieldType.Float) else style1
                sheet.write(main_row, col_main, v, styleTemp)
            main_row += 1

    def run(self):
        if len(self.tableInfos) == 0:
            return
        fileName_choose, filetype = QFileDialog.getSaveFileName(
            self.MainForm,
            "Export To Excel File Name",
            getcwd(),  # 起始路径
            "Excel Files (*.xls)")
        if not fileName_choose:
            return
        else:
            self.xlsBook = xlwt.Workbook(encoding='utf-8')  # 新建一个excel

        for i, tab in enumerate(self.tableInfos):
            self.__ExportOneTableInfo(tab, 'sheet{}'.format(i))
        try:
            self.xlsBook.save(fileName_choose)
        except Exception as e:
            errstr = '写入文件出错！\nWrite file error!\n'
            errstr = errstr + Exception.__repr__(e)
            QMessageBox.information(self.MainForm, '提示', errstr)
        QMessageBox.information(self.MainForm, '提示',
                                '导出数据完成！\nExport to excel complete!')
