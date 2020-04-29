import abc
import datetime
import re
from decimal import Decimal
from os import getcwd
from sys import path as jppath

jppath.append(getcwd())

from PyQt5.QtCore import (QAbstractItemModel, QDate, QModelIndex, QObject, Qt,
                          QVariant, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                             QDateEdit, QDialog, QHBoxLayout, QItemDelegate,
                             QLineEdit, QMenu, QMessageBox, QPushButton,
                             QStyledItemDelegate, QStyleOptionViewItem,
                             QTableView, QWidget)

import lib.JPMvc.JPDelegate as myDe
from lib.JPDatabase.Database import JPDb
from lib.JPDatabase.Field import JPFieldType
from lib.JPDatabase.Query import (JPQueryFieldInfo, JPTabelFieldInfo,
                                  JPTabelRowData)
from lib.JPException import JPExceptionFieldNull, JPExceptionRowDataNull
from lib.JPFunction import JPDateConver, JPGetDisplayText
from lib.JPMvc.JPDelegate import _JPDelegate_Base
from lib.JPMvc.JPModel import (JPTableViewModelEditForm,
                               JPTableViewModelReadOnly)
from lib.JPPrint.JPPrintReport import JPReport
from lib.JPPublc import JPPub
from Ui.Ui_FormSearch import Ui_DlgSearch

jppath.append(getcwd())




class myJPTableViewModelEditForm(JPTableViewModelEditForm):
    def __init__(self, tableView, tabelFieldInfo):
        super().__init__(tableView, tabelFieldInfo)
        self.dataChanged.connect(self._whenDataChange)

    def clear456(self, r):
        # 只要修改了字段，清除后三项并禁止编辑
        de = myDe.JPDelegate_ReadOnly(self.tableView)
        self.tableView.setItemDelegateForColumn(4, de)
        self.tableView.setItemDelegateForColumn(5, de)
        self.tableView.setItemDelegateForColumn(6, de)
        self.setData(self.createIndex(r, 4), None)
        self.setData(self.createIndex(r, 5), None)
        self.setData(self.createIndex(r, 6), None)

    def _whenDataChange(self, index):
        pass

    def checkOnRow_(self, row):
        ro = Qt.EditRole
        data3 = self.data(self.createIndex(row, 3), ro)
        data4 = self.data(self.createIndex(row, 4), ro)
        data5 = self.data(self.createIndex(row, 5), ro)
        data6 = self.data(self.createIndex(row, 6), ro)
        if data3 is None or data4 is None:
            return False
        en1 = data4[1]['En1']
        en2 = data4[1]['En2']
        if en1 == 0 and en2 == 0:
            return True
        elif en1 == 1 and en2 == 0:
            if data5:
                return True
        elif en1 == 1 and en2 == 1:
            if data5 and data6:
                return True
        return False

    def afterSetDataBeforeInsterRowEvent(self, row_data, Index):
        return self.checkOnRow_(Index.model().rowCount() - 1)

    def data(self, index, role=Qt.DisplayRole):
        c = index.column()
        r = index.row()
        if role == Qt.DisplayRole and c == 3:
            cell = self.TabelFieldInfo.DataRows[r].Datas[c]
            if cell is None:
                return None
            else:
                result = cell[1][0]
                return result
        elif role == Qt.DisplayRole and c == 4:
            cell = self.TabelFieldInfo.DataRows[r].Datas[c]
            if cell is None:
                return None
            else:
                result = cell[1]["TiC"] + cell[1]["Tie"]
                return result
        elif role == Qt.DisplayRole and c in [5, 6]:
            rowData = self.TabelFieldInfo.DataRows[r].Datas
            v = rowData[c]
            return JPGetDisplayText(v, FieldInfo=self.TabelFieldInfo.Fields[c])
        elif role == Qt.TextAlignmentRole and c in [5, 6]:
            return Qt.AlignCenter
        else:
            return super().data(index, role=role)


class MyButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(MyButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index) and (
                index.row() != index.model().rowCount() - 1):
            widget = QPushButton(self.tr(''),
                                 self.parent(),
                                 clicked=self.parent().cellButtonClicked)
            fn = 'del_line.ico'
            icon = QIcon(getcwd() + "\\res\\ico\\" + fn)
            widget.setIcon(icon)
            self.parent().setIndexWidget(index, widget)

    def createEditor(self, parent, option, index):
        """有这个空函数覆盖父类的函数，才能使该列不可编辑"""
        return

    def setEditorData(self, editor, index):
        return

    def setModelData(self, editor, model, index):
        return


class JDFieldComboBox(QStyledItemDelegate):
    def __init__(self, tab, parent: QObject = None):
        super().__init__(parent)
        self.tableView = parent
        self.tab = tab

    def setDialog(self, dlg):
        self.Dialog = dlg

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:

        list_fld = [[fld.Title, fld.FieldName, fld.TypeCode]
                    for fld in self.tab.Fields]
        wdgt = QComboBox(parent)
        for i, row in enumerate(list_fld):
            wdgt.addItem(row[0], (i, row))
        return wdgt

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        data = index.model().data(index, Qt.EditRole)
        if data is None:
            editor.setCurrentIndex(-1)
        else:
            editor.setCurrentIndex(data[0])
            return

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        if index.column() > 0:
            data = editor.currentData()
            index.model().setData(index, data, Qt.EditRole)
            model.clear456(index.row())
            if data:
                self.Dialog.fieldChange(index, data)

    def updateEditorGeometry(self, editor: QWidget,
                             StyleOptionViewItem: QStyleOptionViewItem,
                             index: QModelIndex):
        editor.setGeometry(StyleOptionViewItem.rect)


class mySYCombobox(QStyledItemDelegate):
    SY_CHAR = (
        {
            "Sy": "`{fieldname}` like '%{value1}%'",
            "En1": 1,
            "En2": 0,
            "TiC": "包含",
            "Tie": "Include"
        },
        {
            "Sy": "`{fieldname}`='{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "等于",
            "Tie": "Equal"
        },
        {
            "Sy": "`{fieldname}`>'{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "大于",
            "Tie": "GreaterThan"
        },
        {
            "Sy": "`{fieldname}`>='{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "大于或等于",
            "Tie": "GreaterOrEqual"
        },
        {
            "Sy": "`{fieldname}`<'{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "小于",
            "Tie": "LessThan"
        },
        {
            "Sy": "`{fieldname}`<='{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "小于或等于",
            "Tie": "LessOrEqual"
        },
        {
            "Sy": "`{fieldname}`<>'{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "不等于",
            "Tie": "NotEqual"
        },
        {
            "Sy": "`{fieldname}` like '{value1}%'",
            "En1": 1,
            "En2": 0,
            "TiC": "开头是",
            "Tie": "BeginLike"
        },
        {
            "Sy": "Not `{fieldname}` like '{value1}%'",
            "En1": 1,
            "En2": 0,
            "TiC": "开头不是",
            "Tie": "NotBeginLike"
        },
        {
            "Sy": "`{fieldname}` like '%{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "结束是",
            "Tie": "EndLike"
        },
        {
            "Sy": "Not `{fieldname}` like '%{value1}'",
            "En1": 1,
            "En2": 0,
            "TiC": "结束不是",
            "Tie": "NotEndLike"
        },
        {
            "Sy": "IsNull(`{fieldname}`)",
            "En1": 0,
            "En2": 0,
            "TiC": "为空",
            "Tie": "IsNull"
        },
        {
            "Sy": "Not IsNull(`{fieldname}`)",
            "En1": 0,
            "En2": 0,
            "TiC": "不为空",
            "Tie": "NotNull"
        },
        #Ext
        {
            "Sy": "LENGTH(`{fieldname}`)={value1}",
            "En1": 1,
            "En2": 0,
            "TiC": "长度为",
            "Tie": "LengthIs"
        },
        {
            "Sy": "LENGTH(`{fieldname}`)>={value1}",
            "En1": 1,
            "En2": 0,
            "TiC": "长度大于等于",
            "Tie": "LengthGreaterOrEqual"
        },
        {
            "Sy": "LENGTH(`{fieldname}`)<={value1}",
            "En1": 1,
            "En2": 0,
            "TiC": "长度小于等于",
            "Tie": "LengthLessOrEqual"
        },
        {
            "Sy": "LENGTH(`{fieldname}`)>{value1}",
            "En1": 1,
            "En2": 0,
            "TiC": "长度大于",
            "Tie": "LengthGreaterThan"
        },
        {
            "Sy": "LENGTH(`{fieldname}`)<{value1}",
            "En1": 1,
            "En2": 0,
            "TiC": "长度小于",
            "Tie": "LengthLessThan"
        },
        {
            "Sy": "`{fieldname}`=''",
            "En1": 0,
            "En2": 0,
            "TiC": "为空字符",
            "Tie": "IsEmptyString"
        })
    SY_BOOL = ({
            "Sy": "`{fieldname}`=1",
            "En1": 0,
            "En2": 0,
            "TiC": "值为是",
            "Tie": "IsTrue"
        }, {
            "Sy": "`{fieldname}`=0",
            "En1": 0,
            "En2": 0,
            "TiC": "值为否",
            "Tie": "ISFalse"
        }, {
            "Sy": "IsNull(`{fieldname}`)",
            "En1": 0,
            "En2": 0,
            "TiC": "为空",
            "Tie": "IsNull"
        }, {
            "Sy": "Not IsNull(`{fieldname}`)",
            "En1": 0,
            "En2": 0,
            "TiC": "不为空",
            "Tie": "NotNull"
        })
    SY_DATE = ({
        "Sy": "`{fieldname}`='{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "等于",
        "Tie": "Equal"
    }, {
        "Sy": "`{fieldname}`<'{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "早于",
        "Tie": "EarluThan"
    }, {
        "Sy": "`{fieldname}`<='{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "早于等于",
        "Tie": "EarlyOrEqual"
    }, {
        "Sy": "`{fieldname}`>'{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "晚于",
        "Tie": "LaterThan"
    }, {
        "Sy": "`{fieldname}`>='{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "晚于等于",
        "Tie": "LaterOrEqual"
    }, {
        "Sy": "`{fieldname}`<>'{value1}'",
        "En1": 1,
        "En2": 0,
        "TiC": "不等于",
        "Tie": "NotEqual"
    }, {
        "Sy": "`{fieldname}` Between '{value1}' And '{value2}'",
        "En1": 1,
        "En2": 1,
        "TiC": "在区间内",
        "Tie": "Between"
    }, {
        "Sy": "Not (`{fieldname}` Between '{value1}' And '{value2}')",
        "En1": 1,
        "En2": 1,
        "TiC": "不在区间内",
        "Tie": "NotBetween"
    }, {
        "Sy": "IsNull(`{fieldname}`)",
        "En1": 0,
        "En2": 0,
        "TiC": "为空",
        "Tie": "IsNull"
    }, {
        "Sy": "Not IsNull(`{fieldname}`)",
        "En1": 0,
        "En2": 0,
        "TiC": "不为空",
        "Tie": "NotNull"
    })
    SY_NUM = ({
        "Sy": "`{fieldname}`={value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "等于",
        "Tie": "Equal"
    }, {
        "Sy": "`{fieldname}`>{value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "大于",
        "Tie": "GreaterThan"
    }, {
        "Sy": "`{fieldname}`>={value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "大于或等于",
        "Tie": "GreaterOrEqual"
    }, {
        "Sy": "`{fieldname}`<{value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "小于",
        "Tie": "LessThan"
    }, {
        "Sy": "`{fieldname}`<={value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "小于或等于",
        "Tie": "LessOrEqual"
    }, {
        "Sy": "`{fieldname}`<>{value1}",
        "En1": 1,
        "En2": 0,
        "TiC": "不等于",
        "Tie": "NotEqual"
    }, {
        "Sy": "`{fieldname}` Between {value1} and {value2}",
        "En1": 1,
        "En2": 1,
        "TiC": "在区间内",
        "Tie": "Between"
    }, {
        "Sy": "Not (`{fieldname}` Between {value1} and {value2})",
        "En1": 1,
        "En2": 1,
        "TiC": "不在区间内",
        "Tie": "NotBetween"
    }, {
        "Sy": "IsNull(`{fieldname}`)",
        "En1": 0,
        "En2": 0,
        "TiC": "为空",
        "Tie": "IsNull"
    }, {
        "Sy": "Not IsNull(`{fieldname}`)",
        "En1": 0,
        "En2": 0,
        "TiC": "不为空",
        "Tie": "NotNull"
    })
    SY = {
        JPFieldType.String: SY_CHAR,
        JPFieldType.Int: SY_NUM,
        JPFieldType.Float: SY_NUM,
        JPFieldType.Boolean: SY_BOOL,
        JPFieldType.Date: SY_DATE
    }

    def __init__(self, typecode, parent=None):
        super().__init__(parent=parent)
        self.tup = self.SY[typecode]

    def setDialog(self, dlg):
        self.Dialog = dlg

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem,
                     index: QModelIndex) -> QWidget:
        wdgt = QComboBox(parent)
        for i, row in enumerate(self.tup):
            wdgt.addItem(row["TiC"] + row["Tie"], (i, row))
        return wdgt

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        data = index.model().data(index, Qt.EditRole)
        if data is None:
            editor.setCurrentIndex(-1)
        else:
            if data[0] > -1:
                editor.setCurrentIndex(data[0])
            return

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        data = editor.currentData()
        index.model().setData(index, data, Qt.EditRole)
        self.Dialog.syChange(index, data)

    def updateEditorGeometry(self, editor: QWidget,
                             StyleOptionViewItem: QStyleOptionViewItem,
                             index: QModelIndex):
        editor.setGeometry(StyleOptionViewItem.rect)


class myTabelFieldInfo(JPTabelFieldInfo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addRow(self):
        if len(self) == 0:
            super().addRow()
        else:
            super().addRow()
            self.DataRows[len(self) - 1].setData(1, "And")


class Form_Search(QDialog):
    whereStringCreated = pyqtSignal(str)

    def __init__(self, tabinfo, base_sql, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.ui = Ui_DlgSearch()
        self.ui.setupUi(self)
        self.tv = self.ui.tableView
        self.BaseSQL = base_sql

        sql = """
        SELECT fID,'' AS Guanxi, '' AS ZuoKuoHao, 
            '' AS Ziduan, '' AS YunSuan, '' AS Zhi1,
            '' AS Zhi2, '' AS YouKuoHao
        FROM sysconfig
        LIMIT 0
        """
        tab = myTabelFieldInfo(sql, True)
        titles = [
            " ", "关系", "(", "字段Field", "运算Symbols", "值1 Value1", "值2 Value2",
            ")"
        ]
        for i, t in enumerate(titles):
            tab.Fields[i].Title = t

        self.tab = tab
        self.tab.addRow()
        self.Model = myJPTableViewModelEditForm(self.tv, self.tab)
        self.tv.setModel(self.Model)
        widths = [30, 50, 50, 150, 150, 100, 100, 50]
        for i, w in enumerate(widths):
            self.tv.setColumnWidth(i, w)
        lst_gx = [['', ''], ['And', 'And'], ['Or', 'Or'], ['Not', 'Not']]
        self.de_sy = myDe.JPDelegate_ComboBox(self.tv, lst_gx)
        self.de_kh_left = myDe.JPDelegate_ComboBox(self.tv, [
            ['', ''],
            ['(', '('],
        ])
        self.de_kh_right = myDe.JPDelegate_ComboBox(self.tv,
                                                    [['', ''], [')', ')']])
        self.de_field = JDFieldComboBox(tabinfo)
        self.de_field.setDialog(self)
        self.tv.setItemDelegateForColumn(3, self.de_field)
        self.de_no = myDe.JPDelegate_ReadOnly(self.tv)
        self.tv.setItemDelegateForColumn(4, self.de_no)
        self.tv.setItemDelegateForColumn(5, self.de_no)
        self.tv.setItemDelegateForColumn(6, self.de_no)
        self.tv.cellButtonClicked = self.cellButtonClicked
        self.tv.setItemDelegateForColumn(0, MyButtonDelegate(self.tv))
        self.setDelegate127(0)
        self.tv.setCurrentIndex(self.Model.createIndex(0, 3))

    def setDelegate127(self, r):
        if r == 0:
            self.tv.setItemDelegateForColumn(1, self.de_no)
            self.tv.setItemDelegateForColumn(7, self.de_no)
        else:
            self.tv.setItemDelegateForColumn(1, self.de_sy)
            self.tv.setItemDelegateForColumn(7, self.de_kh_right)
        self.tv.setItemDelegateForColumn(2, self.de_kh_left)

    def accept(self):
        bz = 1
        rng = self.Model.rowCount() - bz
        if rng == 0:
            txt = '没有输入有效查询条件！\nNo valid query conditions are entered!'
            if QMessageBox.information(self, "提示", txt):
                return
            return
        # 检查括号是否配对
        kh_l = 0
        kh_r = 0
        for i in range(rng):
            if self.tab.DataRows[i].Datas[2]:
                kh_l += 1
            if self.tab.DataRows[i].Datas[7]:
                kh_r += 1
        if kh_l != kh_r:
            txt = "括号不匹配！"
            if QMessageBox.information(self, "提示", txt):
                return
        # 检查每一行是否输入完整
        for i in range(rng):
            row_ok = self.Model.checkOnRow_(i)
            if row_ok is False:
                txt = '第【{n}】行条件输入不完整！\n'
                txt = txt + 'Line [{n}] condition input is incomplete!'
                QMessageBox.information(self, "提示", txt.format(n=i + 1))
                return

        # 开始生成表达式
        lst = []
        for i in range(rng):
            rd = self.tab.DataRows[i]
            temp_exp = rd.Datas[4][1]['Sy'].format(fieldname=rd.Datas[3][1][0],
                                                   value1=rd.Datas[5],
                                                   value2=rd.Datas[6])
            gx = rd.Datas[1] + " " if rd.Datas[1] else ''
            lkh = rd.Datas[2] if rd.Datas[2] else ''
            rkh = rd.Datas[7] if rd.Datas[7] else ''
            temp_exp = gx + lkh + temp_exp + rkh
            lst.append(temp_exp)
        txt = str(' '.join(lst))
        sql = "select QQ_QQ.* from ({base_sql}) as QQ_QQ where ({txt})"
        sql = sql.format(txt=txt, base_sql=self.BaseSQL)
        self.whereStringCreated.emit(sql)
        self.close()

        return

    def cellButtonClicked(self, *args):
        index = self.tv.selectionModel().currentIndex()
        self.Model.TabelFieldInfo.DataRows[index.row() + 1].setData(1, "")
        self.Model.removeRows(index.row(), 1, index)

    def fieldChange(self, index, data):

        if index.column() > 0:
            tp = data[1][2]
            de = mySYCombobox(tp, self.tv)
            de.setDialog(self)
            self.tv.setItemDelegateForColumn(4, de)
            self.setDelegate127(index.row())

    def syChange(self, index, data):
        de_bool = myDe.JPDelegate_ComboBox(self.tv, [['SIM', 1], ['Non', 0]])
        de_date = myDe.JPDelegate_DateEdit(self.tv)
        de_int = myDe.JPDelegate_LineEdit(self.tv, 1)
        de_float = myDe.JPDelegate_LineEdit(self.tv, 2)
        de_str = myDe.JPDelegate_LineEdit(self.tv)
        self.des = {
            JPFieldType.String: de_str,
            JPFieldType.Int: de_int,
            JPFieldType.Float: de_float,
            JPFieldType.Boolean: de_bool,
            JPFieldType.Date: de_date
        }
        if data:
            r = index.row()
            tp = self.tab.DataRows[r].Datas[3][1][2]
            dic = data[1]
            if dic["En1"]:
                self.tv.setItemDelegateForColumn(5, self.des[tp])
            if dic["En2"]:
                self.tv.setItemDelegateForColumn(6, self.des[tp])
            self.setDelegate127(index.row())


if __name__ == "__main__":
    import sys
    db = JPDb()
    db.setDatabaseType(1)
    app = QApplication(sys.argv)
    sql_0 = """
                SELECT fOrderID as 订单号码OrderID,
                        fOrderDate as 日期OrderDate,
                        fCustomerName as 客户名Cliente,
                        fCity as 城市City,
                        fSubmited1 as 提交Submited,
                        fSubmit_Name as 提交人Submitter,
                        fRequiredDeliveryDate as 交货日期RequiredDeliveryDate,
                        fAmount as 金额SubTotal,
                        fDesconto as 折扣Desconto,
                        fTax as 税金IVA,
                        fPayable as `应付金额Valor a Pagar`,
                        fContato as 联系人Contato,
                        fCelular as 手机Celular,
                        fSubmited AS fSubmited,
                        fEntry_Name as 录入Entry
                FROM v_order AS o"""
    aaa = JPTabelFieldInfo(sql_0)
    s = Form_Search(JPTabelFieldInfo(sql_0, True), sql_0)
    s.exec_()

    db = JPDb()
    db.setDatabaseType(1)
    sql = "select '' as Guanxi,'' as ZuoKuoHao, '' as Ziduan, '' as YunSuan,'' as Zhi1,'' as Zhi2, '' as YouKuoHao,fID from sysconfig Limit 0 "
    tab = JPTabelFieldInfo(sql, True)
    del tab.Fields[0]
    a = 1
