import sys
# sys.path.append('E: \projectM')

from PyQt5.QtSql import QSqlRelationalDelegate, QSqlTableModel
from PyQt5 import QtSql, QtCore, QtWidgets
from PyQt5.QtWidgets import (QWidget,
                             QLabel, QComboBox, QDataWidgetMapper,
                             QApplication, QDialog)

from lib.JPDatabase.Database import JPDb
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import (Qt, QRect, pyqtSlot, QModelIndex,
                          QAbstractTableModel, QVariant,
                          QSize, QAbstractItemModel)
from lib.JPDevelopmenter.Ui.Ui_FormReportManage import Ui_Dialog
from functools import singledispatch
from enum import IntEnum
from PyQt5.QtPrintSupport import QPrinter
import logging


def _lstPaperSize():
    return [[5, 'A0', '841 x 1189 mm'],
            [6, 'A1', '594 x 841 mm'],
            [7, 'A2', '420 x 594 mm'],
            [8, 'A3', '297 x 420 mm'],
            [0, 'A4', '210 x 297 mm, 8.26 x 11.69 英寸'],
            [9, 'A5', '148 x 210 mm'],
            [10, 'A6', '105 x 148 mm'],
            [11, 'A7', '74 x 105 mm'],
            [12, 'A8', '52 x 74 mm'],
            [13, 'A9', '37 x 52 mm'],
            [14, 'B0', '1000 x 1414 mm'],
            [15, 'B1', '707 x 1000 mm'],
            [16, 'B10', '31 x 44 mm'],
            [17, 'B2', '500 x 707 mm'],
            [18, 'B3', '353 x 500 mm'],
            [19, 'B4', '250 x 353 mm'],
            [1, 'B5', '176 x 250 mm, 6.93 x 9.84 英寸'],
            [20, 'B6', '125 x 176 mm'],
            [21, 'B7', '88 x 125 mm'],
            [22, 'B8', '62 x 88 mm'],
            [23, 'B9', '33 x 62 mm'],
            [24, 'C5E', '163 x 229 mm'],
            [25, 'Comm10E', '105 x 241 mm, U.S. Common 10 Envelope'],
            [30, 'Custom', 'Unknown, or a user defined size.'],
            [26, 'DLE', '110 x 220 mm'],
            [4, 'Executive', '7.5 x 10 英寸, 190.5 x 254 mm'],
            [27, 'Folio', '210 x 330 mm'],
            [44, 'JisB6', ''],
            [28, 'Ledger', '431.8 x 279.4 mm'],
            [3, 'Legal', '8.5 x 14 英寸, 215.9 x 355.6 mm'],
            [2, 'Letter', '8.5 x 11 英寸, 215.9 x 279.4 mm'],
            [29, 'Tabloid', '279.4 x 431.8 mm'],
            ]
    # def setItemDelegate(self, _JPRelationalDelegate: _JPRelationalDelegate)


class _JPRelationalDelegate(QSqlRelationalDelegate):
    def __init__(self, parent: QWidget, mapper: QDataWidgetMapper):
        '''自定义有外键的单表编辑代理\n
        调用方法：\n
        Mapper.setItemDelegate(parent:窗体,mapper:QDataWidgetMapper)\n
        参数：\n
        parent为编辑窗体,mapper中存放窗体的数据model，所以必须传递
        '''
        self.mapper = mapper
        super().__init__(parent=parent)

    def setEditorData(self, QWidget, QModelIndex):
        '''当编辑窗口的基础model的当前行变化时，设置控件值'''
        if isinstance(QWidget, QComboBox):
            model = QWidget.model()
            for i in range(model.rowCount()):
                if QModelIndex.data() == model.data(
                        model.createIndex(i, 0), Qt.EditRole):
                    QWidget.setCurrentIndex(i)
        else:
            return super().setEditorData(QWidget, QModelIndex)

    def setModelData(self, editor: QWidget,
                     model: QAbstractItemModel,
                     index: QModelIndex):
        '''保存前更新基础model的数据'''
        mapperModel = self.mapper.model()
        mapperIndex = mapperModel.createIndex(
            self.mapper.currentIndex(), index.column())

        if isinstance(editor, QtWidgets.QComboBox):
            mod = editor.model()
            data = mod.dataList[editor.currentIndex()][mod.modelColumn]
            mapperModel.setData(mapperIndex, data)
        else:
            super().setModelData(editor, model, index)
        mapperModel.dataChanged.emit(mapperIndex, mapperIndex)


class _JPComboBoxModel(QAbstractTableModel):
    def __init__(self, parent=None,
                 dataList: list = [],
                 displayColumn: int = 0,
                 modelColumn: int = 1):
        '''返回一个用于关系数据QComboBox对象的数据模型'''
        self.dataList = dataList
        self.displayColumn = displayColumn
        self.modelColumn = modelColumn
        super().__init__(parent=parent)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.dataList)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def data(self, QModelIndex, role=Qt.DisplayRole):
        x = QModelIndex.row()
        if role == Qt.DisplayRole:
            return self.dataList[x][self.displayColumn]
        elif role == Qt.EditRole:
            return self.dataList[x][self.modelColumn]
        else:
            return QVariant()


class JPMainTableModel(QtSql.QSqlRelationalTableModel):
    # _tp中存放需要添加到数据映射器中的控件类型
    # 要添加的控件，必须用字段名命名(大小写敏感)
    _tp = (QtWidgets.QLineEdit, QtWidgets.QDateEdit, QtWidgets.QComboBox,
           QtWidgets.QTextEdit, QtWidgets.QCheckBox, QtWidgets.QSpinBox)

    def __init__(self, parent: QWidget, tableName: str,
                 filter: str = None, db=QtSql.QSqlDatabase()):
        '''用于窗体模式进行数据编辑时的主窗体数据模型。\n
        会自动增加数据映射器，但是外键字段要使用addComboBoxData方法增加列表文字。
        最后要调用tofirst()方法定位编辑的记录。\n
        注：数据映射器不能增删记录，只能编辑
        '''
        super().__init__(parent=parent, db=db)
        self.parent = parent
        self.setTable(tableName)
        if filter:
            self.setFilter(filter)
        self.select()
        rec = self.record()
        self.mapper = QDataWidgetMapper(parent)
        self.mapper.setModel(self)
        self.mapper.setItemDelegate(
            _JPRelationalDelegate(parent, self.mapper))
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        for i in range(rec.count()):
            widget = parent.findChild(self._tp, rec.fieldName(i))
            if widget:
                if not isinstance(widget, QComboBox):
                    self.mapper.addMapping(widget, i)

    def toFirst(self):
        # 定位到模型中第一条记录
        self.mapper.toFirst()

    def addComboBoxData(self, fieldName: str,
                        dataList: list,
                        displayColumn: int = 0,
                        modelColumn: int = 1):
        '''给模型中添加一个QComboBox控件的数据源。\n
        dataList为行来源数据源，列表对象.\n
        displayColumn为Combobox中要显示文字位于列表中的列号(首列为0)\n
        modelColumn为要保存到模型中数据在列表中的列号(首列为0)\n
        '''
        widget = self.parent.findChild(QComboBox, fieldName)
        if widget is not None:
            widget.setModel(_JPComboBoxModel(
                widget, dataList, displayColumn, modelColumn))
            self.mapper.addMapping(widget, self.fieldIndex(fieldName))

    def saveData(self):
        pass


class JpSubTableModel(QSqlTableModel):
    # 统计信息信号，只有添加了统计列才会发送此信号
    # 信号的三个参数分别为：统计字段名、统计类型、统计值
    StatisticsValueChange = QtCore.pyqtSignal(str, int, float)
    Sum = 0
    Max = 1
    Min = 2
    Average = 3

    def __init__(self, parent: QWidget,
                 tableName: str,
                 tableView: QtWidgets.QTableView,
                 parentPkFieldName: str = '',
                 db=QtSql.QSqlDatabase()):
        '''用于使用tableView显示一个表中的数据，也可以作为主子表情况下子表数据模型。\n
        可以设置统计列数据（StatisticsValueChange信号会传递相关结果）;
        也可能加一些计算列（addViewColumn方法增加列时，省略fieldIndex参数会被认为只计算列）
        '''
        super().__init__(parent=parent, db=db)
        self._tableView = tableView
        # 存放tableView中要显示的列的信息
        self._columnInfomation: list = []
        # 存放用户增加的统计列的信息
        self._StatisticsColumn: list = []
        self._parentPkFieldName = parentPkFieldName
        self.setTable(tableName)
        self.setEditStrategy(QSqlTableModel.OnRowChange)
        self.beforeInsert.connect(self._beforeInsert)
        self._setPrimaryKeyInfomation()

    def _setPrimaryKeyInfomation(self):
        ''''查找表的主键信息'''
        record = self.record()
        for i in range(len(record)):
            fld = record.field(i)
            if fld.isAutoValue():
                self._primaryKeyLocation = i
                self._primaryKeyName = fld.name()
                return

    def addViewColumn(self,
                      header: str,
                      fieldName: str,
                      Align: Qt.AlignmentFlag = Qt.AlignLeft,
                      formatString: str = ''):
        '''给tableView中增加要显示的的一个列
        参数 formatString '{:,.2f}' 分节符两位小数
        '''
        found = self.fieldIndex(fieldName)
        fieldIndex = -1 if found is None else found
        self._columnInfomation.append(
            [header, fieldIndex, Align, formatString])

    def columnCount(self, parent=QModelIndex()):
        return len(self._columnInfomation)

    def addStatisticsColumn(self, fieldName: str, mode):
        '''增加一个统计列\n
        mode可取值：JpSubTableModel.Sum;
        JpSubTableModel.Max;
        JpSubTableModel.Min;
        JpSubTableModel.Average。
        '''
        col = self.fieldIndex(fieldName)
        self._StatisticsColumn.append([fieldName, col, mode])

    # def flags(self, index):
    #     return Qt.NoItemFlags
    def select(self):
        result = super().select()
        for r in self._StatisticsColumn:
            self._StatisticsAndEmit(r[1])
        return result

    def data(self, index: QtCore.QModelIndex, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        # 防止读取大于设定列的数据
        if index.column() > (len(self._columnInfomation)-1):
            return super().data(index, role=role)
        y = self._columnInfomation[c][1]
        if role == Qt.DisplayRole:
            formatString = self._columnInfomation[c][3]
            v = None
            # 计算列的情形
            if y == -1:
                try:
                    v = self.calculateCell(self.record(r), index)
                except Exception:
                    logging.getLogger().warning(
                        "第{}行[{}]计算错误".format(r, self._columnInfomation[c][0]))
                    v = None
            # 非计算列的情形
            else:
                v = super().data(self.createIndex(r, y), role=role)
            # 格式化
            if formatString and v:
                return formatString.format(v)
            else:
                if v is not None:
                    return str(v)
                else:
                    return QVariant()
        elif role == Qt.EditRole:
            if y != -1:
                return super().data(self.createIndex(r, y), role=role)
            else:
                return QVariant()
        elif role == Qt.TextAlignmentRole:
            return self._columnInfomation[c][2]
        else:
            return super().data(index, role=role)
        return super().data(index, role=role)

    def setData(self, index: QModelIndex, Any, role=Qt.EditRole):
        if role == Qt.EditRole:
            y = self._columnInfomation[index.column()][1]
            modelIndex = self.createIndex(index.row(), y)
            super().setData(modelIndex, Any, role=role)
            # 统计并发射统计信号
            self._StatisticsAndEmit(y)
            self.dataChanged.emit(modelIndex, modelIndex)
            return True
        return False

    def connectNotify(self, signal):
        # 当信号被绑定到一个函数时，模型中存在数据时，发送一次信号
        if (QtCore.QMetaMethod(signal).name() == b'StatisticsValueChange'
                and self.rowCount() > 0):
            for r in self._StatisticsColumn:
                self._StatisticsAndEmit(r[1])
        return super().connectNotify(signal)

    def _StatisticsAndEmit(self, column: int):
        # 任何setData方法后，内部计算统计并发射统计信号
        for s in self._StatisticsColumn:
            fieldName = s[0]
            modelColumn = s[1]
            mode = s[2]
            result = 0.0
            data = []
            if modelColumn == column:
                for i in range(self.rowCount()):
                    temp = self.record(i).value(modelColumn)
                    data.append(temp if temp else 0.0)
                if mode == JpSubTableModel.Sum:
                    result = sum(data)
                if mode == JpSubTableModel.Average:
                    result = sum(data)//len(data)
                if mode == JpSubTableModel.Min:
                    result = min(data)
                if mode == JpSubTableModel.Max:
                    result = max(data)
                self.StatisticsValueChange.emit(fieldName, mode, result)

    def calculateCell(self, record: QtSql.QSqlRecord,
                      index: QtCore.QModelIndex):
        '''如果有计算列，此函数要覆盖，此函数返回计算列的值\n
        参数：index要计算的值位于tableView中的位置用于判断\n
        record当前记录的值用于计算
        '''
        lst = [r for r in self._columnInfomation if r[1] == -1]
        s = ('存在计算列，但没有实现calculateCell函数。'
             '该函数给定当前行数据及列名，应该返回计算列的值')
        if lst:
            raise UserWarning(s)

    def parentTableRowChanged(self, parentPkValue: int = 0):
        '''槽函数，用于主表当前行变化时更新视图数据\n
        此函数接收一个值，为主表主键值
        '''
        pkn=self._parentPkFieldName
        self.setFilter("{}={}".format(pkn,parentPkValue))
        self.select()
        self.resetInternalData()

    def headerData(self, col: int, QtOrientation, role=Qt.DisplayRole):
        if QtOrientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columnInfomation[col][0]
        else:
            return super().headerData(col, QtOrientation, role=role)
    def remo
    def appendRow(self):
        '''在末尾增加一行，增加前调用beforeInsertRowCheckData函数检查尾行合法性'''
        if self.rowCount() == 0:
            return super().insertRow(self.rowCount())
        if self.beforeInsertRowCheckData(self.record(self.rowCount()-1)):
            result = super().insertRow(self.rowCount())
            if result:
                self._tableView.selectRow(self.rowCount())
            return False
        else:
            return False

    def _beforeInsert(self, record: QtSql.QSqlRecord):
        if self.filter():
            fn, fv = self.filter().split('=')
            record.setValue(fn, int(fv))
            record.setGenerated(fn, True)

    def beforeInsertRowCheckData(self, lastRecord: QtSql.QSqlRecord):
        '''增加新行前检查最后一行数据的有效性'''
        s = ('没有重写增加新行前的检查函数,'
             'lastRecord参数为最后一行的数据用于判断'
             '本函数返回值为True时增加行')
        raise UserWarning('没有重写增加新行前的检查函数,本函数返回值为True时增加行')


class myLabel(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.mousePressed = False
        self.x: int = None
        self.y: int = None
        self.rect: QRect = None

    def mouseMoveEvent(self, e):
        if self.mousePressed:
            x = e.pos().x()
            y = e.pos().y()
            print('move old x={},y={};new x={},y={}'.format(self.x, self.y, x, y))
            newx = self.rect.x()+(x-self.x)
            newy = self.rect.y()+(y-self.y)
            self.setGeometry(newx, newy, self.rect.width(), self.rect.height())
            self.rect = self.geometry()
            self.x = x
            self.y = y

        return super().mouseMoveEvent(e)

    def mousePressEvent(self, e):
        self.mousePressed = True
        self.x = e.pos().x()
        self.y = e.pos().y()
        print('Press old x={},y={};new x={},y={}'.format(self.x, self.y, 0, 0))
        self.rect = self.geometry()
        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, QMouseEvent):
        self.mousePressed = False
        return super().mouseReleaseEvent(QMouseEvent)


class mySubTableModel(JpSubTableModel):
    def calculateCell(self, record, index):
        return (record.value(10)+record.value(11)+record.value(12)+record.value(13))

    def beforeInsertRowCheckData(self, rec):
        if not all((rec.field(11).value(), rec.field(12).value(), rec.field(13).value(), rec.field(10).value())):
            print("fX不能为0")
        else:
            return True


class myReportUi():
    def __init__(self):
        # my_JPRelationalDelegate = _JPRelationalDelegate()
        self.ui = Ui_Dialog()
        self.Dialog = QDialog()
        self.ui.setupUi(self.Dialog)
        self.initReportSelecter1()
        self.ui.ReportSelect1.currentIndexChanged[int].connect(
            self.ReportChange1)
        self.ui.butSaveReport.clicked.connect(self.SaveReport)
        self.ui.butAddReport.clicked.connect(self.addReport)
        self.ui.butDeleteReport.clicked.connect(self.delReport)
        self.addMode = False
        self.ModelReport = JPMainTableModel(self.Dialog, 'sysreports')
        zhixing = [['{} {}'.format(r[1], r[2]), r[0]] for r in _lstPaperSize()]
        self.ModelReport.addComboBoxData('fReportPaperSize', zhixing)
        self.ModelReport.addComboBoxData(
            'fReportPaperOrientation', [['横排', 1], ['竖排', 0]])
        self.ModelReport.toFirst()
        # self.subModel=QSqlTableModel(self.Dialog)
        # self.subModel.setTable('sysreports')
        # self.subModel.setFilter('fReportPk=1')
        # self.subModel.select()
        # self.ui.tableView.setModel(self.subModel)

        self.subModel = mySubTableModel(
            self.Dialog, 'sysreports', self.ui.tableView, 'fReportPk')
        self.subModel.addViewColumn(
            "编号", 'pk', Qt.AlignRight | Qt.AlignVCenter)
        self.subModel.addViewColumn(
            "条目名称", 'fItemName')
        self.subModel.addViewColumn(
            "左", 'fX', Qt.AlignRight | Qt.AlignVCenter, '{:,.2f}')
        self.subModel.addViewColumn(
            "右", 'fY', Qt.AlignRight | Qt.AlignVCenter, '{:,.2f}')
        self.subModel.addViewColumn(
            "上", 'fWidth', Qt.AlignRight | Qt.AlignVCenter, '{:,.2f}')
        self.subModel.addViewColumn(
            "下", 'fHeight', Qt.AlignRight | Qt.AlignVCenter, '{:,.2f}')
        self.subModel.addViewColumn(
            "计算", '', Qt.AlignRight | Qt.AlignVCenter, '{:,.2f}')
        self.subModel.addStatisticsColumn("fX", JpSubTableModel.Sum)
        self.subModel.setFilter('fReportPk=1')
        self.subModel.select()
        # print(self.subModel.record(0).field(0).value())
        self.ui.tableView.setModel(self.subModel)
        self.subModel.StatisticsValueChange.connect(self.tongji)
        self.ui.butAddItem.clicked.connect(self.subAddRow)
        self.ui.butSaveSubTable.clicked.connect(self.SaveSubTable)

    def SaveSubTable(self):
        print("子表脏数据", self.subModel.isDirty())
        self.subModel.submitAll()

    def subAddRow(self):
        self.subModel.appendRow()

    def tongji(self, fieldname, mode, result):
        self.ui.lineEditTongJi.setText(str(result))

    def test(self, *arg):
        mod = self.ui.fReportPaperSize.model()
        print(self.ui.fReportPaperSize.currentData())
        print(arg)

    def show(self):
        self.Dialog.show()

    def delReport(self):
        self.relationModel.mask = True
        # print(self.relationModel.isDirty())
        return
        row = self.Mapper.currentIndex()
        self.ModelReport.removeRow(row)
        self.ModelReport.submitAll()
        if row+1 > self.ModelReport.rowCount():
            row = self.ModelReport.rowCount()-1
        self.Mapper.setCurrentIndex(row)
        self.addMode = False

    def addReport(self):
        row = self.ModelReport.rowCount()
        self.ModelReport.insertRow(row)
        self.ModelReport.mapper.setCurrentIndex(row)
        self.ui.fIsReport.setChecked(True)
        self.addMode = True

    def SaveReport(self):
        print("脏数据", self.ModelReport.mapper.model().isDirty())
        row = self.ModelReport.mapper.currentIndex()
        result = self.ModelReport.mapper.submit()
        self.ModelReport.submitAll()

        print(str(QtSql.QSqlDatabase().lastError().text()))
        # self.ModelReport.submitAll()
        # self.Mapper.setCurrentIndex(row)
        # if self.addMode:
        #     if result:
        #         self.initReportSelecter1()
        #         sql = 'SELECT LAST_INSERT_ID()'
        #         query = QtSql.QSqlQuery()
        #         query.exec(sql)
        #         if query.next():
        #             for i in range(self.ui.ReportSelect1.count()):
        #                 if self.ui.ReportSelect1.itemData(i) == query.value(0):
        #                     self.ui.ReportSelect1.setCurrentIndex(i)
        #     self.addMode = False
        print(result)

    def ReportChange1(self, index):
        pk = self.ui.ReportSelect1.currentData()
        self.subModel.parentTableRowChanged(pk)
        for i in range(self.ModelReport.rowCount()):
            index = self.ModelReport.createIndex(i, 0)
            if int(self.ModelReport.data(index, Qt.EditRole)) == pk:
                self.ModelReport.mapper.setCurrentIndex(i)
                # self.ui.fReportPaperSize.setCurrentIndex(10)

    def initReportSelecter1(self):
        sql = 'select pk,fItemName from sysreports where isnull(fReportPk)'
        query = QtSql.QSqlQuery()
        query.exec(sql)
        while (query.next()):
            self.ui.ReportSelect1.addItem(query.value(
                'fItemName'), query.value('pk'))

    # def initReportView(self):
    #     self.Model = QtSql.QSqlRelationalTableModel()
    #     self.Model.setTable('v_sysreport')
    #     Relation = QtSql.QSqlRelation("t_enumeration", "fItemID", "fTitle")
    #     self.Model.setRelation(3, Relation)
    #     self.Model.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
    #     self.tableViewReport.setModel(self.Model)
    #     self.header = ['编号',
    #                    '名称',
    #                    '纸型',
    #                    '方向',
    #                    '联次信息',
    #                    '左',
    #                    '上',
    #                    '右',
    #                    '下']
    #     for i, r in enumerate(self.header):
    #         self.Model.setHeaderData(i, QtCore.Qt.Horizontal, r)
    #     self.Model.select()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # QPrinter.Landscape, QPrinter.Portrait)
    JPDb().getQSqlDatabase()
    ui = myReportUi()
    ui.show()
    sys.exit(app.exec_())
