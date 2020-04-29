# -*- coding: utf-8 -*-

import abc
import datetime
import itertools
from decimal import Decimal
from enum import IntEnum

from PyQt5.QtCore import QDate, QMargins, QRect, Qt
from PyQt5.QtGui import (QColor, QFont, QFontMetrics, QPainter, QPixmap,
                         QTransform)
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog


class JPPrintSectionType(IntEnum):
    """本类为节类型的枚举"""
    ReportHeader = 1
    PageHeader = 2
    Detail = 0
    PageFooter = 3
    ReportFooter = 4
    GroupHeader = 5
    GroupFooter = 6

    @staticmethod
    def GetSectionName(i: int):
        str = ['主体', '报表页眉', '页面页眉', '页面页脚', '报表页脚', '组页眉', '组页脚']
        return str[i]


class JPPrintError(Exception):
    def __init__(self, msg: str):
        self.Msg = msg


class _jpPrintItem(metaclass=abc.ABCMeta):
    # Report = None  # 类属性，打印条目属于的报表对象
    # TotalPagesCalculated = False

    def __init__(self, rect, PrintObject, **kwargs):
        if self.Report is None:
            raise JPPrintError("Report属性没有设置，无法继续")
        self.Section = kwargs.get("Section", None)
        self.AutoLineBreak = kwargs.get("AutoLineBreak", False)
        self.Rect: QRect = rect
        self.PrintObject = PrintObject
        self.Bolder = kwargs.get("Bolder", True)
        self.Font = kwargs.get("Font", QFont("Microsoft YaHei", 11))
        self.AlignmentFlag: Qt.AlignmentFlag = kwargs.get(
            "AlignmentFlag", Qt.AlignHCenter)
        # 是否文本右转90度（纵向打印）
        self.Transform = kwargs.get("Transform", False)
        self.FormatString = kwargs.get("FormatString", '{}')
        self.FillColor = kwargs.get("FillColor", None)
        self.Visible = True
        # 是否在文本长度超出指定宽度时，自动截断加上省略号
        self.AutoEllipsis = kwargs.get("AutoEllipsis", False)
        # 是否在文本长度超出指定宽度时，自动缩小字号
        self.AutoShrinkFont = kwargs.get("AutoShrinkFont", False)
        self.Tag = kwargs.get("Tag", None)

    @abc.abstractmethod
    def GetPrintText(self) -> str:
        pass

    def SetAlignment(self, AlignmentFlag: Qt.AlignmentFlag):
        """指定对齐方式"""
        self.AlignmentFlag = AlignmentFlag

    def _NewRect(self, m, o):
        r = self.Rect
        return QRect(r.x() + m.left, r.y() + o + m.top, r.width(), r.height())

    def Print(self, p: QPainter, m: QMargins, o: int = 0):
        if _jpPrintItem.TotalPagesCalculated is False:
            return
        if self.Visible is False:
            return

        r1, r2 = self.Report.onBeforePrint(
            self.Report._CurrentCopys, self.Section,
            self.Section._GetCurrentPrintDataRow(), self)
        if r1:
            return
        txt = r2 if not (r2 is None) else self.GetPrintText()
        rect = self._NewRect(m, o)
        # 填充颜色
        if self.FillColor:
            p.fillRect(rect, self.FillColor)
        # 绘制边框及文本
        if self.Bolder or self.FillColor:
            p.drawRect(rect)
            rect = rect - QMargins(1, 1, 1, 1)
        p.setFont(self.Font)

        if self.Transform:
            FontHeight = QFontMetrics(self.Font).height()
            p.save()
            p.translate(self.Rect.x() + m.left + FontHeight,
                        self.Rect.y() + m.top + o)
            # 第一个参数为距离
            p.rotate(90)
            p.drawText(QRect(0, 0, self.Rect.width(), self.Rect.height()),
                       self.AlignmentFlag, txt)
            # 第一个参数Left为调整后距离页面顶端的距离
            p.restore()
        else:
            fm = p.fontMetrics()
            # 处理长文本省略
            if self.AutoEllipsis:
                elidedText = fm.elidedText(txt, 1, rect.width())
            # 处理长文本自动缩小字体
            if self.AutoShrinkFont:
                self.__AutoShrinkFont(p, rect, txt)
            p.drawText(rect, self.AlignmentFlag,
                       (elidedText if self.AutoEllipsis else txt))

    def __AutoShrinkFont(self, p: QPainter, rect: QRect, txt: str):
        # 循环减小字体适应宽度
        c_Font = p.font()
        c_Size = c_Font.pointSize()
        fm = p.fontMetrics()
        w = fm.width(txt)
        r_w = rect.width()
        while w > r_w:
            c_Size -= 1
            c_Font.setPointSize(c_Size)
            p.setFont(c_Font)
            fm = p.fontMetrics()
            w = fm.width(txt)


class _jpPrintLable(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def GetPrintText(self) -> str:
        if self.PrintObject:
            return self.FormatString.format(self.PrintObject)
        else:
            return ''


class _jpPrintPageField(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def GetPrintText(self):
        try:
            return self.FormatString.format(
                Page=_jpPrintSection.Report._CurrentPage,
                Pages=_jpPrintSection.Report.PageCount)
        except Exception:
            return 'ForamtString Error'


class _jpPrintDateTime(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def GetPrintText(self):
        try:
            return datetime.datetime.now().strftime(self.FormatString)
        except Exception:
            return 'ForamtString Error'


class _jpPrintField(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        self._formula = None
        super().__init__(*args, **kwargs)

    @property
    def Formula(self):
        return self._formula

    @Formula.setter
    def _(self, formula: str):
        """
        设置计算字段，值为一个字符串，计算字段必须有意义，否则可能产生不可预料的错误
        计算字段格式如下：
        数值计算-- 如：'{filedname1}*({filedname1}+{fieldname3})'
        """
        self._formula = formula

    def GetPrintText(self):
        try:
            Ori_v = self.Section._GetCurrentPrintDataRow()[self.PrintObject]
            if Ori_v:
                if isinstance(Ori_v, (int, float)):
                    return self.FormatString.format(Ori_v)
                elif isinstance(Ori_v, QDate):
                    new_v = datetime.datetime(Ori_v.year(), Ori_v.month(),
                                              Ori_v.day()).date()
                    return self.FormatString.format(new_v)
                elif isinstance(Ori_v, Decimal):
                    new_v = float(Ori_v.to_eng_string())
                else:
                    new_v = Ori_v
                return self.FormatString.format(Ori_v)
            else:
                print("数据源中没有找到字段'{}',请检查相关指定数据源的语句！".format(self.PrintObject))
                return ''
        except (KeyError, TypeError):
            return ''


class _jpPrintRowCount(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__currentRow = 0

    def Print(self, painter, Margins, SectionPrintBeginY, currentRow):
        self.__currentRow = currentRow
        super().Print(painter, Margins, SectionPrintBeginY)

    def GetPrintText(self):
        return str(self.__currentRow)


class _jpPrintPixmap(_jpPrintItem):
    def __init__(self, rect, obj, **kwargs):
        img = QPixmap(obj)
        super().__init__(rect, img, **kwargs)

    def Print(self, painter, *args):
        if _jpPrintItem.TotalPagesCalculated is False:
            return
        if self.Visible is False:
            return
        r1, r2 = self.Report.onBeforePrint(
            self.Report._CurrentCopys, self.Section,
            self.Section._GetCurrentPrintDataRow(), self)
        if r1:
            return
        obj = r2 if isinstance(r2, QPixmap) else self.PrintObject
        if _jpPrintItem.TotalPagesCalculated:
            painter.drawPixmap(self._NewRect(args[0], args[1]), obj)

    def GetPrintText(self) -> str:
        pass


class _jpPrintSection(object):
    """本类描述一个打印的节,抽象类，请不要实例化"""

    # Report = None  # 类属性，节所属的报表对象

    def __init__(self):
        self.Items: _jpPrintItem = []
        self._Height = 0

    def __len__(self):
        """节中打印条目的个数"""
        return len(self.Items)

    def _index(self):
        pass

    @abc.abstractmethod
    def Print(self, painter):
        pass

    def OnFormat(self, Section=None, CurrentPrintRow: dict = {}):
        """
        节格式化事件的函数，应该对应一个函数，,返回值为True时，本节不打印
        传递参数时请传递如下命名参数
        Section=当前打印的节
        如果是Detail节的格式化事件，加上下面的参数供用户使用
        CurrentPrintRow=当前打印的行
        接收参数请使用以下格式 OnFormat(self,*args,**kwargs)
        """
        pass

    @property
    def SectionHeight(self):
        return self._Height

    def AddItemRect(self, objtype, rect: QRect, obj, **kwargs) -> _jpPrintItem:
        """
        添加一个单独的打印条目\n
        objtype 取值 1-4。1：标签；2：图片；3：字段；4：页码或时间\n
        x, y, w, h 分别为 左，上，宽，高。注意对于文本，y值指 BaseLine的y坐标
        obj 为内容，对应objtype值如下。
            1：标签文本；字符串对象 ; 2：图片路径或QPixmap对象； 3：字段名称；4：页码；5：日期时间 
        其他命名参数：\n
            Font=QFont 对象 
            FormatString='' 格式字符串。应用于字符串format方法 
                日期时间或页码页码格式字符串。应用于字符串format方法 如：'第{Page}/{Pages}\n
                时间日期格式字符串。如： "PrintTime: %Y-%m-%d %H:%M:%S"
            AlignmentFlag=Qt.Align 如 (Qt.AlignLeft | Qt.TextWordWrap)为左对齐且自动折行
            Bolder=bool 是否打印边框
            Transform=bool 是否纵向文本,objtype为2时无效

        Transform值为True时：
        w 指的是打印条目的纵向高度（相对于纸张）
        h 指的是打印条目的横向宽度（相对于纸张）
        """
        objcls = [
            _jpPrintLable, _jpPrintPixmap, _jpPrintField, _jpPrintPageField,
            _jpPrintDateTime
        ]
        pitem = objcls[objtype - 1](QRect(*rect),
                                    obj,
                                    Section=self,
                                    **kwargs)
        if pitem.Transform:
            # 旋转文字方向时，高度计算方法为左加宽，也就是算最右
            maxH = pitem.Rect.width() + pitem.Rect.top()
        else:
            maxH = pitem.Rect.height() + pitem.Rect.top()
        if (maxH) > self._Height:
            self._Height = maxH
        self.Items.append(pitem)
        return pitem

    def AddItem(self, objtype, x, y, w, h, obj, **kwargs) -> _jpPrintItem:
        """
        添加一个单独的打印条目\n
        objtype 取值 1-4。1：标签；2：图片；3：字段；4：页码或时间\n
        x, y, w, h 分别为 左，上，宽，高。注意对于文本，y值指 BaseLine的y坐标
        obj 为内容，对应objtype值如下。
            1：标签文本；字符串对象 ; 2：图片路径或QPixmap对象； 3：字段名称；4：页码；5：日期时间 
        其他命名参数：\n
            Font=QFont 对象 
            FormatString='' 格式字符串。应用于字符串format方法 
                日期时间或页码页码格式字符串。应用于字符串format方法 如：'第{Page}/{Pages}\n
                时间日期格式字符串。如： "PrintTime: %Y-%m-%d %H:%M:%S"
            AlignmentFlag=Qt.Align 如 (Qt.AlignLeft | Qt.TextWordWrap)为左对齐且自动折行
            Bolder=bool 是否打印边框
            Transform=bool 是否纵向文本,objtype为2时无效

        Transform值为True时：
        w 指的是打印条目的纵向高度（相对于纸张）
        h 指的是打印条目的横向宽度（相对于纸张）
        """
        objcls = [
            _jpPrintLable, _jpPrintPixmap, _jpPrintField, _jpPrintPageField,
            _jpPrintDateTime
        ]
        pitem = objcls[objtype - 1](QRect(x, y, w, h),
                                    obj,
                                    Section=self,
                                    **kwargs)
        if pitem.Transform:
            # 旋转文字方向时，高度计算方法为左加宽，也就是算最右
            maxH = pitem.Rect.width() + pitem.Rect.top()
        else:
            maxH = pitem.Rect.height() + pitem.Rect.top()
        if (maxH) > self._Height:
            self._Height = maxH
        self.Items.append(pitem)
        return pitem

    def AddPrintLables(self,
                       left,
                       top,
                       height,
                       Texts: list = [str],
                       Widths: list = [int],
                       Aligns: list = [],
                       **kwargs):
        n_texts = len(Texts)
        n_widths = len(Widths)
        n_aligns = len(Aligns)
        msg = '标签数与宽度、对齐数不相等:\n'
        msg = msg + f'标签数为{n_texts};宽度数为{n_widths};对齐数为{n_aligns}'
        msg = msg + '\n' + str(Texts)
        if not (n_texts > 0 and n_texts == n_widths and n_texts == n_aligns):
            raise JPPrintError(msg)
        leftSum = 0
        for i in range(n_texts):
            pitem = self.AddItem(1, left + leftSum, top, Widths[i], height,
                                 Texts[i], **kwargs)
            pitem.SetAlignment(Aligns[i])
            leftSum += Widths[i]

    def AddPrintFields(self,
                       left,
                       top,
                       height,
                       FieldNames: list = [str],
                       Widths: list = [int],
                       Aligns: list = [],
                       **kwargs):
        n_fields = len(FieldNames)
        n_widths = len(Widths)
        n_aligns = len(Aligns)
        msg = '字段数与宽度、对齐数不相等:\n'
        msg = msg + f'字段数为{n_fields};宽度数为{n_widths};对齐数为{n_aligns}'
        msg = msg + '\n' + str(FieldNames)
        if not (n_fields > 0 and n_fields == n_widths
                and n_fields == n_aligns):
            raise JPPrintError(msg)
        leftSum = 0
        for i in range(len(FieldNames)):
            pitem = self.AddItem(3, left + leftSum, top, Widths[i], height,
                                 FieldNames[i], **kwargs)
            pitem.SetAlignment(Aligns[i])
            leftSum += Widths[i]

    def _GetCurrentPrintDataRow(self):
        # 当前节为Detail时返回当前正在打印的数据行，否则返回报表数据源第一行
        if self.__dict__["SectionType"] is JPPrintSectionType.Detail:
            return self.__dict__["_CurrentPrintRowData"]
        ds = _jpPrintSection.Report.__dict__['_JPReport' + '__DataSource']
        return ds[0] if len(ds) > 0 else {}

    def _RaisePrintError(self):
        estr = "节【{}】的超出页面可打印范围".format(
            JPPrintSectionType.GetSectionName(self.__dict__["SectionType"]))
        raise JPPrintError(estr)


class _SectionAutoPaging(_jpPrintSection):
    """定义一个自动分页的节，实现，请不要实例化"""
    def __init__(self):
        #  当前页面条目打印时的向下偏移量
        self._CurPageOffset = 0
        #  止上页本节所有已打印项目的总高度
        self._SectionOffset = 0
        super().__init__()

    def Print(self, painter):
        rpt = self.Report
        self._SectionOffset = 0
        self._CurPageOffset = rpt._SectionPrintBeginY
        if rpt.onFormat(self.SectionType, rpt._CurrentPage) or len(self) == 0:
            return
        lastItem = None
        for item in self.Items:
            if item.Visible is False:
                continue
            item_bottom = item.Rect.top() + item.Rect.height()
            # 计算当面页面扣除页脚高度后，还能否容纳当前条目，如不能则进行分页
            if (self._CurPageOffset + item_bottom - self._SectionOffset) > (
                    rpt.PageValidHeight - rpt.PageFooter.SectionHeight):
                self._SectionOffset = item.Rect.top()
                rpt.NewPage(painter)
                self._CurPageOffset = rpt._SectionPrintBeginY
            item.Print(painter, rpt.Margins,
                       -1 * self._SectionOffset + self._CurPageOffset)
            # 纵向打印的不参与计算SectionPrintBeginY

            if item.Transform is False:
                lastItem = item
        # 打印完所有条目后，为下一节保存开始位置，存放于报表对象中
        rpt._SectionPrintBeginY += (lastItem.Rect.top() +
                                    lastItem.Rect.height() -
                                    self._SectionOffset)


class _jpSectionReportHeader(_SectionAutoPaging):
    """报表、组页头类"""
    def __init__(self):
        self.SectionType = JPPrintSectionType.ReportHeader
        super().__init__()

    def Print(self, painter):
        super().Print(painter)


class _jpSectionReportFooter(_SectionAutoPaging):
    """报表、组页脚类"""
    def __init__(self):
        self.SectionType = JPPrintSectionType.ReportFooter
        super().__init__()

    def Print(self, painter):
        #super().Print(painter)
        rpt = self.Report
        curSecH = self.SectionHeight
        if rpt.onFormat(self.SectionType, rpt._CurrentPage) or len(self) == 0:
            return

        # 判断页面剩余空间能否容纳页脚节高度及页脚高度，不能则分页
        if rpt.PageValidHeight < (rpt._SectionPrintBeginY + curSecH +
                                  rpt.PageFooter.SectionHeight):
            rpt.NewPage(painter)
            rpt._SectionPrintBeginY = rpt.PageHeader.SectionHeight
        for item in self.Items:
            item.Print(painter, rpt.Margins, rpt._SectionPrintBeginY)
        rpt._SectionPrintBeginY += curSecH


class _jpSectionDetail(_jpPrintSection):
    def __init__(self):
        self.SectionType = JPPrintSectionType.Detail
        super().__init__()

    def addPrintRowCountItem(self, x, y, w, h, **kwargs):
        """添加一个行号项目，用于打印当前明细数据打印行数"""
        pitem = _jpPrintRowCount(QRect(x, y, w, h),
                                 'PrintRowCount',
                                 Section=self,
                                 **kwargs)
        self.Items.append(pitem)
        return pitem

    def Print(self, painter, sec_data={}):
        rpt = self.Report
        curSecH = self.SectionHeight
        if rpt.onFormat(self.SectionType, rpt._CurrentPage) or len(self) == 0:
            return
        # 判断一下能否同时容纳主体节、页面页眉、页面页脚，不能容纳则抛出错误

        if rpt.PageValidHeight < (curSecH + rpt.PageHeader.SectionHeight +
                                  rpt.PageFooter.SectionHeight):
            self._RaisePrintError()
        if sec_data:
            for i, row in enumerate(sec_data):
                self._CurrentPrintRowData = row
                if rpt.onFormat(self.SectionType, rpt._CurrentPage, row):
                    continue
                # 判断页面剩余空间能否容纳一个节高度及页脚高度，不能则分页
                if rpt.PageValidHeight < (rpt._SectionPrintBeginY + curSecH +
                                          rpt.PageFooter.SectionHeight):
                    rpt.NewPage(painter)
                    rpt._SectionPrintBeginY = rpt.PageHeader.SectionHeight
                for item in self.Items:
                    if isinstance(item, _jpPrintRowCount):
                        item.Print(painter, rpt.Margins,
                                   rpt._SectionPrintBeginY, i + 1)
                    else:
                        item.Print(painter, rpt.Margins,
                                   rpt._SectionPrintBeginY)
                rpt._SectionPrintBeginY += curSecH


class _jpSectionPageHeader(_jpPrintSection):
    def __init__(self):
        self.SectionType = JPPrintSectionType.PageHeader
        super().__init__()

    def Print(self, painter):
        rpt = self.Report
        if rpt.onFormat(self.SectionType, rpt._CurrentPage) or len(self) == 0:
            return
        # 判断当前页面剩余空间能否容纳本节，如不能则引发错误
        if rpt.PageValidHeight < (rpt._SectionPrintBeginY +
                                  self.SectionHeight):
            self._RaisePrintError()
        for item in self.Items:
            if item.Visible is False:
                continue
            item.Print(painter, rpt.Margins, rpt._SectionPrintBeginY)
        rpt._SectionPrintBeginY = self.SectionHeight


class _jpSectionPageFooter(_jpPrintSection):
    def __init__(self):
        self.SectionType = JPPrintSectionType.PageFooter
        super().__init__()

    def Print(self, painter):
        rpt = self.Report
        if rpt.onFormat(self.SectionType, rpt._CurrentPage) or len(self) == 0:
            return
        # 判断当前页面剩余空间能否容纳本节，如不能则引发错误
        if rpt.PageValidHeight < (rpt._SectionPrintBeginY +
                                  self.SectionHeight):
            self._RaisePrintError()
            # 处理打印页脚打印时的开始点
        rpt._SectionPrintBeginY = (rpt.__dict__["_JPReport__PageHeight"] -
                                   self.SectionHeight - rpt.Margins.bottom -
                                   rpt.Margins.top)
        for item in self.Items:
            if item.Visible is False:
                continue
            item.Print(painter, rpt.Margins, rpt._SectionPrintBeginY)
        rpt._SectionPrintBeginY = 0


class _jpGroupCalcField(_jpPrintItem):
    def __init__(self, *args, **kwargs):
        self._index = None
        super().__init__(*args, **kwargs)
        # 存放分组后每组，该计算字段的结果,键值为一个元组
        # 元组的成员为字段分组字段值的组合，顺序为从最高级的分组开始

    def _Value(self, v):
        if v is None:
            return 0
        else:
            return v

    def _Print(self, painter):
        pass

    @abc.abstractmethod
    def Calc(self, row):
        pass

    def Print(self, *args, **kwargs):
        if self._index not in self.Section._KeyPathValues[
                self.Section._CurrentPrintKeys]:
            return
        super().Print(*args, **kwargs)

    def _GetKeyPath(self, row):
        return self.Section._ParentGroup._GetKeyPath(row)

    def GetPrintText(self):
        tup = self.Section._KeyPathValues[self.Section._CurrentPrintKeys][
            self._index]
        return self.FormatString.format(tup)


class _jpGroupCalcField_Sum(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if row[fn] is None:
            return
        v = row[fn]
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: v}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = v
        else:
            tup = sec_kv[KeyPath][CalcIndex]
            sec_kv[KeyPath][CalcIndex] = tup + v


class _jpGroupCalcField_Count(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: 1}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = 1
        else:
            tup = sec_kv[KeyPath][CalcIndex]
            sec_kv[KeyPath][CalcIndex] = tup + 1


class _jpGroupCalcField_Average(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        v = self._Value(row[fn])
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: (v, 1)}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = (v, 1)
        else:
            tup = sec_kv[KeyPath][CalcIndex]
            sec_kv[KeyPath][CalcIndex] = (tup[0] + v, tup[1] + 1)

    def GetPrintText(self):
        # 平均数计算方式不同，本方法重载
        tup = self.Section._KeyPathValues[self.Section._CurrentPrintKeys][
            self._index]
        return self.FormatString.format(tup[0] / tup[1])


class _jpGroupCalcField_Max(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if row[fn] is None:
            return
        v = row[fn]
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: v}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = v
        elif sec_kv[KeyPath][CalcIndex] > v:
            sec_kv[KeyPath][CalcIndex] = v


class _jpGroupCalcField_Min(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if row[fn] is None:
            return
        v = row[fn]
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: v}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = v
        elif sec_kv[KeyPath][CalcIndex] < v:
            sec_kv[KeyPath][CalcIndex] = v


class _jpGroupCalcField_First(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if row[fn] is None:
            return
        v = row[fn]
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: v}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = v


class _jpGroupCalcField_Last(_jpGroupCalcField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Calc(self, row):
        fn = self.PrintObject
        sec_kv = self.Section._KeyPathValues
        CalcIndex = self._index
        KeyPath = self._GetKeyPath(row)
        if row[fn] is None:
            return
        v = row[fn]
        if KeyPath not in sec_kv:
            sec_kv[KeyPath] = {CalcIndex: v}
        elif CalcIndex not in sec_kv[KeyPath]:
            sec_kv[KeyPath][CalcIndex] = v
        else:
            sec_kv[KeyPath][CalcIndex] = v


class _jpGroupSection(_SectionAutoPaging):
    def __init__(self):
        self._ParentGroup = None
        self._CurrentPrintKeys = None
        self._KeyPathValues = {}
        super().__init__()

    def AddCaluField(self, CalcMode: int, x, y, w, h, CalcFieldName, **kwargs):
        '''
        添加一个组内计算字段。CalcMode为计算类型，值如下\n
        Sum = 0; Count = 1;Average = 2; Max = 3; Min = 4 ; First=5 ; Last=6\n
        CalcFieldName为计算的字段。\n
        注意Sum计算需要CalcFieldName为一个数值型字段
        '''
        tempclses = [
            _jpGroupCalcField_Sum, _jpGroupCalcField_Count,
            _jpGroupCalcField_Average, _jpGroupCalcField_Max,
            _jpGroupCalcField_Min, _jpGroupCalcField_First,
            _jpGroupCalcField_Last
        ]
        if CalcMode not in range(0, len(tempclses)):
            return
        pitem = tempclses[CalcMode](QRect(x, y, w, h), CalcFieldName, **kwargs)
        pitem.Section = self
        pitem._index = len(self.Items)
        self.Items.append(pitem)

    def Calc(self, row):
        CalcFlds = [
            item for item in self.Items if isinstance(item, _jpGroupCalcField)
        ]
        # 防止没有计算字段时，无法生成键值
        # self._KeyPathValues[self._ParentGroup._GetKeyPath(row)] = {}
        for i in CalcFlds:
            i.Calc(row)

    def Print(self, painter, curKey):
        if len(self) == 0:
            return
        if (self._KeyPathValues is None) or (len(
                self.Items) == 0) or (curKey not in self._KeyPathValues):
            return
        self._CurrentPrintKeys = curKey
        super().Print(painter)


class _jpPrintGroup(object):
    Report = None

    def __init__(self, GroupByFieldName):
        self.GroupByFieldName = GroupByFieldName
        self.Parent = None
        self.GroupHeader = _jpGroupSection()
        self.GroupHeader._ParentGroup = self
        self.GroupHeader.SectionType = JPPrintSectionType.GroupHeader
        self.GroupFooter = _jpGroupSection()
        self.GroupFooter._ParentGroup = self
        self.GroupFooter.SectionType = JPPrintSectionType.GroupFooter
        self.OrderByField = None

    def _GetKeyPath(self, row):
        tup = str(row[self.GroupByFieldName])
        if self.Parent is self.Report:
            return tup
        else:
            return self.Parent._GetKeyPath(row), tup

    def _GetGroupFieldsPath(self):
        tup = self.GroupByFieldName
        if self.Parent is self.Report:
            return tup
        else:
            return self.Parent._GetGroupFieldsPath(), tup

    def Calc(self, row):
        self.GroupHeader.Calc(row)
        self.GroupFooter.Calc(row)
        if self.Report is self.Parent:
            return
        else:
            self.Parent.Calc(row)
        return

    # 取得子分组
    def _GetSubGroup(self):
        grps = self.Report.__dict__["_JPReport__Groups"]
        for i in range(len(grps)):
            if grps[i] is self:
                if i == (len(grps) - 1):
                    return None
                else:
                    return grps[i + 1]

    def Print(self, painter, **kwargs):
        rpt = self.Report
        data = rpt.DataSource

        if len(kwargs) == 0:
            Keys = sorted(self.GroupHeader._KeyPathValues)
        else:
            Keys = [
                x for x in self.GroupHeader._KeyPathValues
                if x[0] == kwargs['Key']
            ]
        subGrp = self._GetSubGroup()
        kp = self._GetGroupFieldsPath()

        def myfilter(row, key):
            for i in range(len(kp)):
                if str(row[kp[i]]) != key[i]:
                    return False
            return True

        for k in Keys:
            self.GroupHeader.Print(painter, k)
            if subGrp is None:
                sec_data = [r for r in data if myfilter(r, k)]
                rpt.Detail.Print(painter, sec_data)
            else:
                subGrp.Print(painter, Key=k)
            self.GroupFooter.Print(painter, k)


class _JPPrintPreviewDialog(QPrintPreviewDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def open(self):
    #     print("afadsfasdf")

    # def done(self,int1):
    #     print(int1)


class JPReport(object):
    """报表类"""
    def __init__(self, PaperSize, Orientation):
        _jpPrintSection.Report = self
        _jpPrintItem.Report = self
        _jpPrintGroup.Report = self
        _jpPrintItem.TotalPagesCalculated = False
        self.PaperSize = PaperSize
        self.Orientation = Orientation
        self.Margins: QMargins = QMargins(0, 0, 0, 0)
        self.ReportHeader = _jpSectionReportHeader()
        self.ReportFooter = _jpSectionReportFooter()
        self.PageHeader = _jpSectionPageHeader()
        self.PageFooter = _jpSectionPageFooter()
        self.Detail = _jpSectionDetail()
        self.ReportHeader.Report = self
        self.ReportFooter.Report = self
        self.PageHeader.Report = self
        self.PageFooter.Report = self
        self.Detail.Report = self
        self.Copys = 1
        self._CurrentPage = 0
        self._CurrentCopys = 0
        self.__PageCount = 0
        self.__Groups = []
        self.__DataSource = {}
        self.__Errors = []
        self.__Printer: QPrinter = None
        self.__PageHeight = None
        self.__Calculated = False
        self.__Reseted = False
        self.__SectionPrintBeginY = 0
        self.__ExecNewPageTimes = 0

    def onFormat(self,
                 SectionType: JPPrintSectionType,
                 CurrentPage: int,
                 RowDate=None):
        """
        请在子类中覆盖本方法
        本方法为报表类各节的格式化事件，返回值为False或None时，
        当前节或Detail节的本行数据不打印，其他值均正常打印。
        """
        name = SectionType.GetSectionName()
        msg = f'[{name}节的format事件没有重写!]'
        print(msg)
        return True

    def onBeforePrint(self, Copys, Sec, CurrentPrintDataRow, obj):
        """一个条目的打印前事件,可以重写此方法
        传递参数：
        1、当前Copy数；2、当前打印的节；3、当前打印的行数据(对于Detail节)
        4、当前打印对象 
        要求的返回值：
        第一个值为True时，将取消打印事件
        第二个值有返回值时，将用此返回值做为最终打印的文本,
        """
        return False, None

    # def __del__(self):
    #     _jpPrintSection.Report = None
    #     _jpPrintItem.Report = None
    #     _jpPrintGroup.Report = None

    @property
    def _SectionPrintBeginY(self):
        return self.__SectionPrintBeginY

    @_SectionPrintBeginY.setter
    def _SectionPrintBeginY(self, top: int):
        self.__SectionPrintBeginY = top

    @property
    def PageCount(self):
        return self.__PageCount

    @PageCount.setter
    def PageCount(self, num):
        if _jpPrintItem.TotalPagesCalculated is False:
            self.__PageCount = num

    def AddGroup(self, GroupFieldName: str) -> _jpPrintGroup:
        """添加一个组，参数是组名"""
        grp = _jpPrintGroup(GroupFieldName)
        grp.Report = self
        if len(self.__Groups) == 0:
            grp.Parent = self
        else:
            grp.Parent = self.__Groups[len(self.__Groups) - 1]
        self.__Groups.append(grp)
        return grp

    def _Calc_All_Fields(self):
        if len(self.__Groups) == 0:
            return
        if self.__Calculated is True:
            return
        grpEnd = self.__Groups[len(self.__Groups) - 1]
        for row in self.__DataSource:
            grpEnd.Calc(row)
        self.__Calculated = True

    @property
    def PageValidHeight(self) -> int:
        return self.__PageHeight - self.Margins.top - self.Margins.bottom

    @property
    def DataSource(self) -> dict:
        """返回报表数据源"""
        return self.__DataSource

    @DataSource.setter
    def DataSource(self, data: dict):
        """报表数据源属性，参数为一个字典"""
        self.__DataSource = data

    @property
    def Errors(self):
        return self.__Errors

    def SetMargins(self, top=0, left=0, right=0, bottom=0):
        """设置纸边距"""
        self.Margins.top = top
        self.Margins.left = left
        self.Margins.right = right
        self.Margins.bottom = bottom

    @property
    def Printer(self) -> QPrinter:
        return self.__Printer

    @Printer.setter
    def Printer(self, Printer):
        # 重置相关内部属性，恢复页码，设置纸型
        self.CurrentPage = 0
        self._CurrentCopys = 0
        if self.__Reseted is False:
            self.PageCount = 0
        self._SectionPrintBeginY = 0
        self.__Printer = Printer
        if self.__Reseted is False:
            self.__Printer.setPaperSize(self.PaperSize)
            self.__Printer.setOrientation(self.Orientation)
            self.__Reseted = True
        pageRect = self.__Printer.pageRect()
        self.__PageHeight = pageRect.height()

    def NewPage(self, painter) -> int:
        """创建一个新页，设置下页打印开始位置为页面起始位置"""
        if _jpPrintItem.TotalPagesCalculated and self.__ExecNewPageTimes > 0:
            self.__Printer.newPage()
        self._SectionPrintBeginY = 0
        self._CurrentPage += 1
        self.PageCount += 1
        self.PageFooter.Print(painter)
        self.PageHeader.Print(painter)

        self.__ExecNewPageTimes += 1
        print("self.__ExecNewPageTimes=" + str(self.__ExecNewPageTimes))

    def __PrintOrCalcOneCopy(self, painter):
        """打印或计算一次报表"""
        # 重新打印或计算页码时，总页码清零 这是2019.09.05最后加上的
        self.PageCount = 0
        self.NewPage(painter)
        self.PageFooter.Print(painter)
        self.ReportHeader.Print(painter)
        if len(self.__Groups) == 0:
            # 没有分组时，直接打明细
            self.Detail.Print(painter, self.__DataSource)
        else:
            for grp in self.__Groups:
                grp.Print(painter)
        self.ReportFooter.Print(painter)

    def PrintPreview(self, printer: QPrinter):
        """PrintPreview方法会自动接收一个参数 ，参数为QPrinter对象"""
        self.Printer = printer
        printer.Unit = QPrinter.Millimeter
        painter = QPainter(printer)
        painter.restore()
        _jpPrintItem.TotalPagesCalculated = False
        # 第一遍打印用于计算总页数，其后打印进行实际绘制
        self.__PrintOrCalcOneCopy(painter)
        self.__ExecNewPageTimes = 0
        _jpPrintItem.TotalPagesCalculated = True
        for i in range(self.Copys):
            self._CurrentPage = 0
            self._CurrentCopys += 1
            self.__PrintOrCalcOneCopy(painter)

    def BeginPrint(self):
        if len(self.__Errors):
            return
        # 打印之前先进行分组字段的计算，并修改计算完成标志
        # 放到此处是为了防止用户在修改纸型等打印参数时引发重算
        self._Calc_All_Fields()

        # 后台用用户定义的纸型及边距计算一次页码，注意过程中不用真正绘制
        dialog = _JPPrintPreviewDialog(self.Printer)
        dialog.paintRequested.connect(self.PrintPreview)

        dialog.exec_()
