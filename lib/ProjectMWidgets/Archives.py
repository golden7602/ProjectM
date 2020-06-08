

from .ArchivesEdit import EditForm_Archive
from .LinkList import Node, BilateralLinkList
from PyQt5 import Qt
import logging
import datetime
from dateutil.relativedelta import relativedelta
import time
from PyQt5.QtCore import (QThread, QDate, QMetaObject, QSize, QRect,
                          pyqtSlot, Qt, QModelIndex, pyqtSignal, QObject)
from PyQt5 import QtSql
import fitz
from lib.JPFunction import GetFileMd5, GetStrAsMD5
from threading import Thread
from lib.JPForms.JPFormSearch import Form_Search
from lib.JPDatabase.Query import JPQueryFieldInfo
from Ui.Ui_FormArchivesEdit import Ui_Form as Ui_Form_Edit
from Ui.Ui_FormArchivesList import Ui_Form as Ui_Form_List
from Ui.Ui_FormViewPic import Ui_Dialog as Ui_Dialog_ViewPic
from lib.ProjectMWidgets.SelectProject import FormSelectProject
from lib.JPPublc import JPDb, JPPub, JPUser
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPFunction import JPDateConver
from lib.JPDatabase.Query import JPTabelFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog, QTableWidgetItem, QItemDelegate,
                             QDialog, QLabel, QScrollArea, QVBoxLayout,
                             QAction, QMenu, QProgressDialog,
                             QDesktopWidget)
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QGuiApplication, QCursor)
import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())

# class FormPopProgressBar(QProgressDialog):
#     def __init__(self, parent=None, flags=Qt.WindowFlags()):
#         super().__init__(parent=parent, flags=flags)
#         self.setWindowTitle("请稍候......")
#         # h = 105
#         # w = 560
#         # self.resize(w, h)
#         # self.setMinimumSize(QSize(w, h))
#         # self.setMaximumSize(QSize(w, h))
#         # label = QLabel(self)
#         # self.__label = label
#         # label.setGeometry(QRect(30, 0, 511, 41))
#         # label.setObjectName("label")
#         # label.setText("")
#         # pb = QProgressBar(self)
#         # self.__pb = pb
#         # pb.setGeometry(QRect(20, 60, 520, 23))
#         # pb.setTextVisible(False)
#         # pb.setFormat("")
#         # pb.setObjectName("progressBar")
#         self.setMinimum(0)
#         self.setMaximum(0)
#         self.setValue(0)
#         self.setAutoClose(True)
#         self.setAutoReset(True)
#         # self.center()

#     # @property
#     # def value(self):
#     #     return self.__pb.value()

#     # def open(self):
#     #     self.center()
#     #     super().open()

#     # def center(self):
#     #     screen = QDesktopWidget().screenGeometry()
#     #     size = self.geometry()
#     #     self.move((screen.width() - size.width()) / 2,
#     #               (screen.height() - size.height()) / 2)
#     #     QGuiApplication.processEvents()

#     def reset(self, maxValue=0):
#         self.setMaximum(maxValue)
#         self.setLabelText('准备中.....')
#         super().reset()
#         # self.open()
#         # QGuiApplication.processEvents()

#     def dispInfo(self, text='', value=0):
#         self.setValue(value)
#         if text:
#             self.setLabelText('正在加载【{}】\n请稍候......'.format(text))
#         # QGuiApplication.processEvents()

#     def dispInfoStep(self, text=''):
#         self.dispInfo(text, self.value()+1)


# class Form_ViewPic(QDialog):
#     def __init__(self, parent=None, viewPixmap=None, ViewPdfAndPic=None, flags=Qt.WindowFlags()):
#         pub = JPPub()
#         super().__init__(parent=pub.MainForm, flags=flags)
#         self.ui = Ui_Dialog_ViewPic()
#         self.ui.setupUi(self)
#         self.viewPixmap = viewPixmap
#         self.ui.label.setScaledContents(False)
#         self.setModal(True)
#         self.showMaximized()
#         self.ViewPdfAndPic = ViewPdfAndPic
#         for i, item in enumerate(ViewPdfAndPic):
#             if viewPixmap is item['pixmap']:
#                 self.currentIndex = i
#                 self.DispPicIndex(i)
#                 break

#     def resizeEvent(self, resizeEvent):
#         if self.viewPixmap:
#             self.ui.label.setPixmap(self.viewPixmap.scaledToHeight(
#                 self.ui.label.height(), Qt.SmoothTransformation))

#     def DispPicIndex(self, index):
#         self.setButHide()
#         viewPic = self.ViewPdfAndPic[self.currentIndex]['pixmap']
#         viewPic2 = viewPic.scaledToHeight(
#             self.ui.label.height(), Qt.SmoothTransformation)
#         self.ui.label.setPixmap(viewPic2)

#     def setButHide(self):
#         i = self.currentIndex
#         s = len(self.ViewPdfAndPic)
#         self.ui.butFirst.setEnabled(i != 0 and s > 1)
#         self.ui.butPre.setEnabled(i > 0 and s > 1)
#         self.ui.butNext.setEnabled(i < s-1)
#         self.ui.butLast.setEnabled(i != s-1)

#     @pyqtSlot()
#     def on_butFirst_clicked(self):
#         self.currentIndex = 0
#         self.DispPicIndex(self.currentIndex)

#     @pyqtSlot()
#     def on_butPre_clicked(self):
#         self.currentIndex -= 1
#         self.DispPicIndex(self.currentIndex)

#     @pyqtSlot()
#     def on_butNext_clicked(self):
#         self.currentIndex += 1
#         self.DispPicIndex(self.currentIndex)

#     @pyqtSlot()
#     def on_butLast_clicked(self):
#         self.currentIndex = len(self.ViewPdfAndPic)-1
#         self.DispPicIndex(self.currentIndex)


class MyCopyFileError(Exception):
    def __init__(self, from_path, to_path, old_msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        errstr = "保存文件过程中出现错误,但数据已经成功保存！"
        errstr = errstr + 'An error occurred while saving the file\n'
        errstr = errstr + f'From:{from_path}\n'
        errstr = errstr + f'To:{to_path}\n'
        errstr = errstr + old_msg
        self.errstr = errstr

    def __str__(self):
        return self.errstr


# class myJPTableViewModelReadOnly(JPTableViewModelReadOnly):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.ok_icon = JPPub().MainForm.getIcon('yes.ico')

#     def data(self, index, role=Qt.DisplayRole):
#         r = index.row()
#         c = index.column()
#         if c in (7, 8, 9):
#             if role == Qt.DisplayRole:
#                 return ''
#             if role == Qt.TextAlignmentRole:
#                 return (Qt.AlignLeft | Qt.AlignVCenter)
#             if role == Qt.DecorationRole:
#                 if self.TabelFieldInfo.getOnlyData((r, c)):
#                     return self.ok_icon
#             else:
#                 return super().data(index, role=role)
#         else:
        # return super().data(index, role=role)


class myJPTableViewModelReadOnly(QtSql.QSqlRelationalTableModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ok_icon = JPPub().MainForm.getIcon('yes.ico')

    def data(self, index, role=Qt.DisplayRole):
        r = index.row()
        c = index.column()
        if c == 0 and role == Qt.TextAlignmentRole:
            return (Qt.AlignRight | Qt.AlignVCenter)
        elif c == 1 and role == Qt.DisplayRole:
            return JPDateConver(self.data(index, Qt.EditRole), str)
        elif c in (8, 9, 10):
            if role == Qt.DisplayRole:
                return
            if role == Qt.TextAlignmentRole:
                return (Qt.AlignLeft | Qt.AlignVCenter)
            if role == Qt.DecorationRole:
                if self.data(index, Qt.EditRole) == '\x01':
                    return self.ok_icon
            else:
                return super().data(index, role=role)
        elif c == 11 and role == Qt.DisplayRole:
            if self.data(index, Qt.EditRole) == 0:
                return ''
            else:
                return super().data(index, role=role)
        else:
            return super().data(index, role=role)


# class MyButtonDelegate(QItemDelegate):
#     def __init__(self, parent=None, dataInfo=None):
#         super(MyButtonDelegate, self).__init__(parent)
#         self.dataInfo = dataInfo
#         self.icon = JPPub().MainForm.getIcon('rosette.ico')

#     def paint(self, painter, option, index):
#         curCer = self.dataInfo.DataRows[index.row()].Datas[9]
#         if not self.parent().indexWidget(index) and curCer:
#             widget = QPushButton(
#                 self.tr(''),
#                 self.parent(),
#                 clicked=self.parent().parent().cellButtonClicked)
#             widget.setIcon(self.icon)
#             self.parent().setIndexWidget(index, widget)
#         else:
#             widget = self.parent().indexWidget(index)
#             if widget:
#                 widget.setGeometry(option.rect)

#     def createEditor(self, parent, option, index):
#         """有这个空函数覆盖父类的函数，才能使该列不可编辑"""
#         return

#     def setEditorData(self, editor, index):
#         return

#     def setModelData(self, editor, model, index):
#         return

#     def updateEditorGeometry(self, editor, StyleOptionViewItem,
#                              index: QModelIndex):
#         editor.setGeometry(StyleOptionViewItem.rect)


class Form_Archives(QWidget):
    def __init__(self, mainform):
        super().__init__()
        self.ui = Ui_Form_List()
        self.ui.setupUi(self)
        self.MainForm = mainform
        mainform.addForm(self)
        medit_sql = """
            select archives_pk,
                archive_no,
                issuing_date,
                archive_type,
                archive_describe,
                archive_fulltext,
                issuing,
                title,
                fUserID,
                key_words,is_formalities,is_task_source,is_progress
            from t_archives
            where archives_pk = '{}'"""

        # 设置快速度查询按钮
        icon = QIcon(JPPub().getIcoPath("search.png"))
        action = self.ui.lineEdit.addAction(icon, QLineEdit.TrailingPosition)
        self.ui.lineEdit.returnPressed.connect(self.actionClick)
        self.ui.searchByProject.clicked.connect(self.searchByProject_clicked)
        self.ui.lineEdit.setAttribute(Qt.WA_InputMethodEnabled, True)
        action.triggered.connect(self.actionClick)

        self.SQL_EditForm_Main = medit_sql
        self.lastSearchSQL = ''
        self.pub = JPPub()
        # self.pub.UserSaveData.connect(self.UserSaveData)
        self.ui.tableView.doubleClicked.connect(self.mydoubleClicked)
        JPDb().getQSqlDatabase()
        # q = QtSql.QSqlQuery(sql,db)
        self.Model = myJPTableViewModelReadOnly()
        self.Model.setTable('v_archives')
        # self.Model.setQuery(q)
        Relation = QtSql.QSqlRelation("t_enumeration", "fItemID", "fTitle")
        self.Model.setRelation(3, Relation)
        self.Model.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)

        # 只显示最近一年的记录
        dt = (datetime.date.today() -
              relativedelta(years=1)).strftime("issuing_date>='%Y-%m-%d'")
        self.Model.setFilter(dt)
        # 没有索引无法更新一个单独的行，所以构造了一个索引
        self.Model.setSort(1, Qt.DescendingOrder)
        indexField = self.Model.record().field(0)
        index = QtSql.QSqlIndex()
        index.append(indexField)
        self.Model.setPrimaryKey(index)
        self.header = ['文档编号',
                       '发文日期',
                       '文号',
                       '文件类型',
                       '文件标题',
                       '文档描述',
                       '发文单位',
                       '关键字',
                       '是否手续文件',
                       '是否任务来源',
                       '是否进度文件',
                       '涉及项目数',
                       '涉及项目']
        for i, r in enumerate(self.header):
            self.Model.setHeaderData(i, Qt.Horizontal, r)
        self.ui.tableView.setModel(self.Model)
        self.refreshTableView('')

    def generateMenu(self, pos):
        tv = self.ui.tableView
        mf = JPPub().MainForm
        menu = QMenu()
        item1 = menu.addAction(u"浏览")
        item1.setIcon(mf.getIcon('browse.png'))
        item2 = menu.addAction(u"增加")
        item2.setIcon(mf.getIcon('new.png'))
        menu.addSeparator()
        item3 = menu.addAction(u"编辑")
        item3.setIcon(mf.getIcon('edit.png'))
        item4 = menu.addAction(u"删除")
        item4.setIcon(mf.getIcon('cancel.ico'))

        action = menu.exec_(tv.mapToGlobal(pos))
        if action == item1:
            self.on_CmdBrowse_clicked()
        elif action == item2:
            self.on_CmdNew_clicked()
        elif action == item3:
            self.on_CmdEdit_clicked()
        elif action == item4:
            self.on_CmdDelete_clicked()
        else:
            return

    def mydoubleClicked(self, index):
        self.on_CmdBrowse_clicked()

    def refreshTableView(self, filter: str = ''):
        if filter:
            self.Model.setFilter(filter)
            logging.getLogger().debug(
                "refreshTableView方法刷新了一个过滤条件：{}".format(filter))
        self.Model.select()
        print(self.Model.selectStatement())
        self.ui.tableView.setTextElideMode(Qt.ElideRight)
        # 设置右键菜单
        self.ui.tableView.setContextMenuPolicy(
            Qt.CustomContextMenu)  # 允许右键产生子菜单
        self.ui.tableView.customContextMenuRequested.connect(
            self.generateMenu)  # 右键菜单

        self.ui.tableView.resizeColumnsToContents()

    def actionClick(self):
        txt = self.ui.lineEdit.text()
        if not txt:
            return
        txt = txt.strip()
        txt = txt.replace(' ', "%")
        txt = txt if txt else ''
        filter1 = """
        archive_no like '%{key}%' or
        archive_describe like '%{key}%' or
        issuing like '%{key}%' or
        fTitle like '%{key}%' or
        title like '%{key}%' or
        key_words like '%{key}%' or
        involve_project like '%{key}%'
        """

        filter1 = filter1.format(key=txt)  # archive_fulltext like '%{key}%'
        filter1 = JPDb().getClearSQL(filter1)
        self.refreshTableView(filter1)

    def _refreshRow(self, row):
        self.Model.selectRow(row)

    def _locationRow(self, id):
        rows = self.Model.rowCount()
        for i in range(rows):
            index = self.Model.createIndex(i, 0)
            d = self.Model.data(index)
            if d == id:
                self.ui.tableView.setCurrentIndex(index)

    def refreshTable(self, ID=None):
        # self.ui.lineEdit.setText(None)
        self.refreshTableView()
        if ID:
            self._locationRow(ID)

    def getEditForm(self, sql_main, edit_mode, sql_sub, PKValue):
        frm = EditForm_Archive(sql_main=sql_main,
                               edit_mode=edit_mode,
                               PKValue=PKValue)
        frm.setListForm(self)
        return frm

    def getCurrentSelectPKValue(self):
        index = self.ui.tableView.selectionModel().currentIndex()
        if index.isValid():
            newIndex = self.Model.createIndex(index.row(), 0)
            return self.Model.data(newIndex, Qt.EditRole)

    def searchByProject_clicked(self):
        def searchByProject(lst):
            if not lst:
                return
            txt = 'archives_pk in (select archives_pk from '
            txt = txt + 't_archives_project where project_pk in ({}))'
            txt = txt.format(','.join(lst))
            self.refreshTableView(txt)
        frm = FormSelectProject()
        frm.selectItemChanged.connect(searchByProject)
        frm.show()

    @pyqtSlot()
    def on_CmdSearch_clicked(self):
        dataInfo = JPTabelFieldInfo(self.Model.selectStatement() + " limit 0")
        lst = JPPub().getEnumList(5)
        lst = [[r[0], "'{}'".format(r[0])] for r in lst]
        for i, fld in enumerate(dataInfo.Fields):
            if fld.FieldName == 'fTitle':
                fld.RowSource = lst
                fld.BindingColumn = 1
            fld.Title = self.header[i]
        frm = Form_Search(dataInfo, '')
        frm.whereStringCreated.connect(self.refreshTableView)
        frm.exec_()

    @pyqtSlot()
    def on_CmdRefresh_clicked(self):
        self.refreshTableView()

    @pyqtSlot()
    def on_CmdNew_clicked(self):
        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.New,
                               PKValue=None)
        frm.setListForm(self)
        frm.afterSaveData.connect(self.refreshTable)
        self.__EditForm = frm
        frm.exec_()

    @pyqtSlot()
    def on_CmdBrowse_clicked(self):

        cu_id = self.getCurrentSelectPKValue()
        if not cu_id:
            return

        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.ReadOnly,
                               PKValue=cu_id)
        frm.setListForm(self)
        self.__EditForm = frm
        frm.show()

        # frm.exec_()

    @pyqtSlot()
    def on_CmdExportToExcel_clicked(self):
        TabelFieldInfo = JPTabelFieldInfo(self.Model.selectStatement())
        exp = JPExpExcelFromTabelFieldInfo(TabelFieldInfo,
                                           self.MainForm)
        exp.run()

    @pyqtSlot()
    def on_CmdEdit_clicked(self):
        cu_id = self.getCurrentSelectPKValue()
        index = self.ui.tableView.selectionModel().currentIndex()
        if not cu_id:
            return

        frm = self.getEditForm(sql_main=self.SQL_EditForm_Main,
                               sql_sub=None,
                               edit_mode=JPEditFormDataMode.Edit,
                               PKValue=cu_id)
        frm.setListForm(self)
        frm._currentEditModelRow = index.row()
        frm.currentRowEditComplete.connect(self._refreshRow)
        self.__EditForm = frm
        frm.show()

        # frm.exec_()

    @pyqtSlot()
    def on_CmdDelete_clicked(self):
        uid = self.getCurrentSelectPKValue()
        if uid is None:
            return
        del_txt = '确认要删除此档案？\n请注意，档案附件不会被物理删除!\n'
        sqls = ["delete from t_archives where archives_pk={};".format(uid)]
        temp_sql = "delete from t_additionals_archives where archives_pk={};"
        sqls.append(temp_sql            .format(uid))
        if QMessageBox.question(self, '提示', del_txt,
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            JPDb().executeTransaction(sqls)
            self.refreshTable()


#
# QThread


# class picInfo():
#     def __init__(self):
#         super().__init__()
#         self.Md5Fileindex = 0
#         self.viewPicPath = ''
#         self.pageIndex = 0
#         self.originalNname = ''


# class MyThreadReadAddition(QThread):
#     """加载附件图片的线程类, 每生成一个对象，都通过信号把数据发出
#     本线程只负责从已经加载完成的数据字典中的一行生成图片对象
#     图片的集合应由主界面维护
#     """
#     onePixmCreated = pyqtSignal(dict)
#     oneFileLoaded = pyqtSignal(str)

#     def __init__(self, addtionalData):
#         super().__init__()
#         self.cachePath = os.path.join(os.getcwd(), "cache")
#         if not os.path.exists(self.cachePath):
#             os.mkdir(self.cachePath)
#         self.addtionalData = addtionalData
#         self.defHeight = 200
#         self.pub = JPPub()

#     def render_pdf_page(self, page_data, rowAddtionalData, i):
#         imageFormat = QImage.Format_RGB888
#         pagePixmap1 = page_data.getPixmap(
#             matrix=fitz.Matrix(1, 1),
#             alpha=False)
#         pageQImage1 = QImage(
#             pagePixmap1.samples,
#             pagePixmap1.width,
#             pagePixmap1.height,
#             pagePixmap1.stride,
#             imageFormat)
#         # 生成 pixmap 对象
#         pixmap1 = QPixmap()
#         pixmap1.convertFromImage(pageQImage1)
#         fn = os.path.join(self.cachePath, "{}_{}.jpg".format(
#             GetStrAsMD5(rowAddtionalData['file_name']), i))
#         pixmap1.save(fn, "JPG")
#         temp = picInfo()
#         temp.Md5FileIndex = rowAddtionalData['file_index']
#         temp.pageIndex = i
#         temp.originalNname = rowAddtionalData['file_name']
#         temp.viewPicPath = fn
#         return temp

#     def createEveryPixmapFromFile(self):
#         def readPDF(path, addtionalData):
#             doc = fitz.open(path)
#             for i in range(doc.pageCount):
#                 pageData = doc.loadPage(i)
#                 print(addtionalData)
#                 pixmap = self.render_pdf_page(
#                     pageData, addtionalData, i)
#                 tempDict = {"pixmap": pixmap,
#                             "addtionalData": addtionalData}
#                 self.onePixmCreated.emit(tempDict)
#             doc.close()

#         def readPIC(path, addtionalData):
#             pixmap = QPixmap(path)
#             tempDict = {"pixmap": pixmap,
#                         "addtionalData": addtionalData}
#             self.onePixmCreated.emit(tempDict)

#         def readIco(icoName, addtionalData, filepath):
#             pixmap = QPixmap(self.pub.getIcoPath(icoName))
#             tempDict = {"pixmap": pixmap, "filePath": filepath,
#                         "addtionalData": addtionalData}
#             self.onePixmCreated.emit(tempDict)
#         for i, r in enumerate(self.addtionalData):
#             if r["deleted"]:
#                 continue
#             #################################
#             # 找到要显示文件的真实路径（数据库中已经存在的和新添加的不同，alreadyExist用于防止用户重复添加同一文件）
#             filePath = r["file_name"] if (
#                 r["alreadyExist"] or r['archives_pk']) else r["original_path"]
#             if os.path.exists(filePath):
#                 expName = r["file_type"].upper()
#                 docDic = {"XLS": 0, "XLSX": 0, "DOC": 1,
#                           "DOCX": 1, "ZIP": 2, "RAR": 3}
#                 icoLst = ["excel.png", "word.png", "zip.png", "rar.png"]
#                 if expName in docDic.keys():
#                     readIco(icoLst[docDic[expName]], r, filePath)
#                 elif expName == "PDF":
#                     readPDF(filePath, r)
#                 elif expName in ["JPG", "PNG", "BMP"]:
#                     readPIC(filePath, r)
#             else:
#                 logging.getLogger().error("文件没有找到:{}".format(filePath))
#             self.oneFileLoaded.emit(r['original_name'])

#     def run(self):
#         self.createEveryPixmapFromFile()


# class EditForm_Project(JPFormModelMain):
#     currentRowEditComplete = pyqtSignal(int)

#     def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
#         super().__init__(Ui_Form_Edit(),
#                          sql_main=sql_main,
#                          PKValue=PKValue,
#                          edit_mode=edit_mode,
#                          flags=flags)
#         self.MainForm = JPPub().MainForm
#         self.MainForm.addLogoToLabel(self.ui.label_logo)
#         self.MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
#         self.MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')
#         self._currentEditModelRow = None
#         self.ui.fUserID.hide()
#         self.pop = FormPopProgressBar(self)
#         #self.PB = self.ui.progressBar
#         # self.PB.hide()
#         self.ui.tableWidget_Project.keyList = []
#         self.addtionalInfo = []
#         # 一个只包含PDF页面和图片的列表,由编辑窗体维护，用于放大显示时用
#         self.ViewPdfAndPic = []
#         self.con_path = JPPub().getConfigData()["archives_path"]
#         if self.isNewMode:
#             self.ui.fUserID.setText(str(JPUser().currentUserID()))
#         self.readData()
#         if (not self.isNewMode) and self.ui.archives_pk.text():
#             sql = "select project_pk from "
#             sql = sql + "t_archives_project where archives_pk={}"
#             dic = JPDb().getDict(sql.format(
#                 self.ui.archives_pk.text().replace(",", "")))
#             pros = [str(r['project_pk']) for r in dic]
#             if pros:
#                 self.readProject(pros)

#         self.ui.archives_pk.setEnabled(False)
#         self.ui.issuing_date.setFocus()
#         QGuiApplication.processEvents()
#         # self.repaint()
#         self.readAddtionalFromDatabase()
#         self.initAdditional()

#         # 根据窗体编辑状态设置窗体中按钮的显示状态
#         if self.isReadOnlyMode:
#             self.ui.but_SelectProject.setEnabled(False)
#             # self.ui.btn_Download.setEnabled(False)
#             self.ui.btn_Add.setEnabled(False)
#             self.ui.btn_Delete.setEnabled(False)

#     def closeEvent(self, event):

#         import gc
#         del self.ViewPdfAndPic
#         del self.addtionalInfo
#         gc.collect()
#         event.accept()
#     # def showInfo(self, range):
#     #     self.PB.show()
#     #     self.PB.setRange(0, range)
#     #     self.ui.label_info.show()
#     #     self.ui.textBrowser.clear()
#     #     self.ui.label_info.setText("")

#     # def dispInfo(self, text, value):
#     #     self.ui.label_info.setText(text)
#     #     self.PB.setValue(value)
#     #     self.ui.textBrowser.append(text)
#     #     QGuiApplication.processEvents()

#     # def hideInfo(self):
#     #     self.PB.hide()
#     #     self.PB.hide()
#     #     self.PB.setRange(0, 0)
#     #     self.ui.textBrowser.clear()
#     #     self.ui.label_info.setText("")

#     def initAdditional(self):

#         # def dispOneMessage(filePath):
#         #     self.pop.dispInfo(filePath, self.pop.value+1)
#         if self.addtionalInfo:
#             self.xc = MyThreadReadAddition(self.addtionalInfo)
#             self.xc.onePixmCreated.connect(self.addOnePixmaptoForm)
#             self.xc.oneFileLoaded.connect(self.pop.dispInfoStep)
#             # self.xc.finished.connect(self.DispOK)
#             self.pop.open()
#             self.pop.setMaximum(len(self.addtionalInfo))
#         # QGuiApplication.setOverrideCursor(QCursor(Qt.BlankCursor))
#             self.xc.start()

#     # def DispBegin(self):
#     #     self.setCursor(Qt.WaitCursor)

#     # def DispOK(self):
#     #     self.PB.hide()
#     #     QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
#     #     # self.setCursor(Qt.ArrowCursor)

#     def deleteAddtional(self, fileanme: str):
#         Labels = self.findChildren(
#             QLabel, "loadPic", Qt.FindChildrenRecursively)
#         delLabels = [item for item in Labels if
#                      item.addtionalData["original_name"] == fileanme]
#         for item in delLabels:
#             for r in reversed(self.ViewPdfAndPic):
#                 if r['addtionalData'] is item.addtionalData:
#                     self.ViewPdfAndPic.remove(r)
#             item.hide()

#         lst2 = [item for item in self.addtionalInfo
#                 if item["original_name"] == fileanme]
#         for item in lst2:
#             item["deleted"] = True
#     # from memory_profiler import profile
#     # @profile

#     def addOnePixmaptoForm(self, pixmapinfo: dict):
#         class MyLabel(QLabel):
#             picDeleted = pyqtSignal(str)

#             def __init__(self, *args, **kw):
#                 super().__init__(*args, **kw)
#                 self.setContextMenuPolicy(Qt.CustomContextMenu)
#                 self.customContextMenuRequested.connect(
#                     self.rightMenuShow)  # 开放右键策略
#                 self.viewPixmap = None
#                 self.ViewPdfAndPic = None

#             def rightMenuShow(self, pos):  # 添加右键菜单
#                 menu = QMenu(self)
#                 if self.isEditMode or self.isNewMode:
#                     menu.addAction(QAction('删除', menu))
#                 if self.isReadOnlyMode:
#                     menu.addAction(QAction('下载', menu))
#                 menu.triggered.connect(self.menuSlot)
#                 menu.exec_(QCursor.pos())

#             def mouseDoubleClickEvent(self, e):
#                 if "filePath" in self.__dict__:
#                     self.pop.open()
#                     self.pop.setMaximum(1)
#                     temppath = os.path.join(os.getcwd(), "temp")
#                     topath = os.path.join(temppath,
#                                           os.path.basename(self.filePath))
#                     if not os.path.exists(temppath):
#                         os.makedirs(temppath)
#                     try:
#                         myCopy(self.filePath, topath)
#                         self.pop.dispInfo('', 1)
#                     except PermissionError as identifier:
#                         self.pop.close()
#                         QMessageBox.critical(
#                             self.parent(), "提示", "复制文件失败，可能您已经打开了此文件！")
#                     else:
#                         # self.pop.close()
#                         os.system(topath)

#                 else:
#                     Form_ViewPic(
#                         self, viewPixmap=self.viewPixmap,
#                         ViewPdfAndPic=self.ViewPdfAndPic)

#             def menuSlot(self, act):
#                 if act.text() == '删除':
#                     sname = self.addtionalData["original_name"]
#                     self.picDeleted.emit(sname)
#                 if act.text() == '下载':
#                     return

#         if "filePath" not in pixmapinfo.keys():
#             self.ViewPdfAndPic.append(pixmapinfo)

#         label = MyLabel()
#         label.ViewPdfAndPic = self.ViewPdfAndPic
#         label.isEditMode = self.isEditMode
#         label.isReadOnlyMode = self.isReadOnlyMode
#         label.isNewMode = self.isNewMode
#         # 设置图片自动填充 label
#         label.setScaledContents(False)
#         label.setStyleSheet("border: 1px solid #646464")
#         # 设置图片到label
#         pixmap = pixmapinfo["pixmap"]
#         label.viewPixmap = pixmap
#         label.setPixmap(pixmap.scaledToHeight(
#             200, Qt.FastTransformation))
#         label.setObjectName("loadPic")
#         label.picDeleted.connect(self.deleteAddtional)
#         label.verticalLayout_6 = self.ui.verticalLayout_6
#         label.setToolTip(pixmapinfo['addtionalData']["original_name"])
#         label.addtionalData = pixmapinfo['addtionalData']
#         label.setAlignment(Qt.AlignCenter)
#         self.ui.verticalLayout_6.addWidget(label)
#         QGuiApplication.processEvents()
#         if "filePath" not in pixmapinfo.keys():
#             self.ViewPdfAndPic.append(pixmapinfo)
#         else:
#             label.__dict__["filePath"] = pixmapinfo['filePath']

#     def onGetFieldsRowSources(self):
#         pub = JPPub()
#         return [
#             ('archive_type', pub.getEnumList(5), 1)
#         ]

#     def readProject(self, pklst):
#         self.ui.tableWidget_Project.keyList = pklst
#         sql = """
#             SELECT project_pk,
#                     project_simple_name
#             FROM t_project_base_info
#             WHERE project_pk IN ({})
#             """
#         data = JPDb().getDict(sql.format(','.join(pklst)))
#         tab = self.ui.tableWidget_Project
#         tab.setColumnCount(2)
#         tab.hideColumn(0)
#         tab.clear()
#         tab.setRowCount(0)
#         tab.setHorizontalHeaderLabels(["项目编号", "项目简称"])
#         row = 0
#         for r in data:
#             Rows = tab.rowCount()
#             tab.setRowCount(Rows+1)
#             newItem = QTableWidgetItem(str(r['project_pk']))
#             tab.setItem(row, 0, newItem)
#             newItem = QTableWidgetItem(r['project_simple_name'])
#             tab.setItem(row, 1, newItem)
#             row += 1

#     def readAddtionalFromDatabase(self):
#         """从数据库中加载给定PK的一个文档的所有附件信息到一个列表中"""
#         sql = """
#         select additional_pk,
#             archives_pk,
#             file_index,
#             file_type,
#             file_pk,
#             original_name,
#             '' as original_path,
#             concat('{}/',file_name) as file_name,
#             False as deleted,
#             0 as alreadyExist,
#             0 as alreadyDusplayed
#         from v_additional_archives
#         where archives_pk={}
#         order by file_index
#         """
#         if not self.isNewMode:
#             pk = self.ui.archives_pk.text().replace(",", "")
#             self.addtionalInfo = JPDb().getDict(sql.format(self.con_path, pk))

#     def onFirstHasDirty(self):
#         self.ui.butSave.setEnabled(True)

#     @pyqtSlot()
#     def on_butCancel_clicked(self):
#         self.close()

#     @pyqtSlot()
#     # 已经调试 增加一个附件
#     def on_btn_Add_clicked(self):
#         def getExName(filepath):
#             t = filepath.split(".")
#             return t[len(t)-1]

#         def md5Exist(filepath: str):
#             """检查文件是否在数据库中已经存在"""
#             sql = """select file_Pk,
#                         concat('{}/',file_name) as file_name,
#                         file_type
#                     from v_additional_archives
#                     where filemd5=unhex('{}') limit 1;"""
#             md5BaseName = GetFileMd5(filepath)
#             md5FileName = '.'.join((md5BaseName, getExName(filepath)))
#             lst = JPDb().getDataList(sql.format(self.con_path, md5BaseName))
#             exist = True if lst else False
#             return exist, md5FileName, md5BaseName, lst if exist else None
#         fileName_choose, filetype = QFileDialog.getOpenFileNames(
#             self,
#             "Select a File",
#             JPPub().getOrSetlastOpenDir(),  # 起始路径
#             "Files (*.jpg *.PDF *.doc *.docx *.xls *.xlsx)")
#         if fileName_choose:
#             JPPub().getOrSetlastOpenDir(fileName_choose[0])
#         for i, original_path in enumerate(fileName_choose):
#             self.ui.archive_describe.append(os.path.basename(original_path))
#             self.pop.dispInfo(original_path, i)
#             dicrow = {'additional_pk': None,
#                       'archives_pk': None,
#                       'file_index': 0,
#                       'original_name': '',
#                       'original_path': '',
#                       'file_type': '',
#                       'file_name': '',
#                       'deleted': 0,
#                       'alreadyExist': 0,
#                       'filemd5': ''}
#             # 检查文件是不是刚刚在窗体中增加过一次
#             upLoadFile = [r['original_path']
#                           for r in self.addtionalInfo if not r['archives_pk']]
#             if original_path in upLoadFile:
#                 self.ui.Label_Info.setText(
#                     "文件【{}】刚刚已经增加".format(original_path))
#                 continue
#             # 检查要上传的文件在数据库中是不是已经存在
#             exist, md5FileName, md5BaseName, lst = md5Exist(original_path)
#             if exist:
#                 dicrow["alreadyExist"] = lst[0][0]
#                 dicrow["file_name"] = lst[0][1]
#                 dicrow["file_type"] = lst[0][2]
#                 dispTxt = "【{}】文件在数据库中存在，已经用数据库中文件替代显示！"
#                 self.ui.Label_Info.setText(
#                     dispTxt.format(os.path.basename(original_path)))
#             else:
#                 dicrow["filemd5"] = md5BaseName
#                 dicrow["file_type"] = getExName(md5FileName)
#                 dicrow["file_name"] = os.path.join(self.con_path, md5FileName)
#                 dicrow["original_path"] = original_path
#                 dicrow["original_name"] = os.path.basename(original_path)

#             self.addtionalInfo.append(dicrow)
#             self.initAdditional()
#             self.firstHasDirty.emit()

#     @pyqtSlot()
#     # 已经调试
#     def on_but_SelectProject_clicked(self):
#         rows = self.ui.tableWidget_Project.rowCount()
#         sels = [self.ui.tableWidget_Project.item(
#             i, 0).text() for i in range(rows)]
#         frm = FormSelectProject(sels)
#         frm.selectItemChanged.connect(self.readProject)
#         frm.show()
#         self.firstHasDirty.emit()

#     @pyqtSlot()
#     # 已经调试
#     def on_btn_Download_clicked(self):
#         # self.setCursor(Qt.WaitCursor)
#         tm = time.strftime('%Y%m%d%H%M%S', time.localtime())
#         uid = JPUser().currentUserID()
#         initPath = "{}_{}".format(uid, tm)
#         temppath = os.getcwd()+"/temp"
#         topath = os.path.join(temppath, initPath)
#         if not os.path.exists(topath):
#             os.makedirs(topath)
#         lst = [item for item in self.addtionalInfo if not item['deleted']]
#         copylst = []
#         for i, item in enumerate(lst):
#             if item['archives_pk']:
#                 fr = os.path.join(self.con_path, item["file_name"])
#                 to = os.path.join(topath, item["original_name"])
#                 copylst.append([fr, to])
#             else:
#                 fr = item["original_path"]
#                 to = os.path.join(topath, item["original_name"])
#                 copylst.append([fr, to])
#         pop = FormPopProgressBar(self)
#         pop.showInfo(len(copylst)-1)
#         for r in copylst:
#             pop.dispInfo("复制{}".format(r[1]), i)
#             myCopy(r[0], r[1])
#         pop.close()
#         txt = '文件保存在：【{}】,点击确定打开该文件夹！'.format(topath)
#         if QMessageBox.question(self,
#                                 '完成',
#                                 txt,
#                                 (QMessageBox.Yes | QMessageBox.No),
#                                 QMessageBox.Yes) == QMessageBox.Yes:
#             topath1 = os.path.abspath(topath)
#             os.system("start explorer {}".format(topath1))

#         # self.setCursor(Qt.ArrowCursor)

#     @pyqtSlot()
#     def on_butSave_clicked(self):
#         try:
#             s1 = self.getSqls(self.PKRole)
#         except Exception as e:
#             t = '生成保存档案数据SQL命令出错，错误信息：\n{}'
#             msgBox = QMessageBox(QMessageBox.Critical, u'提示', t.format(str(e)))
#             msgBox.exec_()
#             return

#         try:
#             s2 = self.CopyPicAndGetSaveFileSQL()
#         except Exception as e:
#             t = '复制文件或生成保存文件数据SQL命令出错，错误信息：\n{}'
#             msgBox = QMessageBox(QMessageBox.Critical, u'提示', t.format(str(e)))
#             msgBox.exec_()
#             return
#         pkSQL = []
#         if self.isNewMode:
#             sPK = JPDb().LAST_INSERT_ID_SQL()
#             pkSQL.append("{} into @archives_pk;".format(sPK))
#         if self.isEditMode:
#             cur_pk = self.ui.archives_pk.text().replace(",", "")
#             pkSQL.append('Select {} into @archives_pk;'.format(cur_pk))
#         # 更新关联项目的SQL
#         up_projectSQL = self. getUpdateProjectSQL()
#         # 拼接所有SQL
#         SQLS = s1[0:len(s1)-1] + pkSQL + up_projectSQL + s2
#         SQLS.append("Select @archives_pk;")

#         # 执行sql
#         try:
#             isOK, result = JPDb().executeTransaction(SQLS)
#             if isOK:
#                 self.ui.butSave.setEnabled(False)
#                 self.afterSaveData.emit(result)
#                 self.currentRowEditComplete.emit(self._currentEditModelRow)
#                 QMessageBox.information(self, '完成',
#                                         '保存数据完成！\nSave data complete!')
#         except Exception as e:
#             msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
#             msgBox.exec_()
#         finally:
#             self.close()

#     def getUpdateProjectSQL(self):
#         result = []
#         if self.isEditMode:
#             delSQL = """delete from t_archives_project 
#                         where archives_pk=@archives_pk;"""
#             result.append(delSQL)
#         for pk in self.ui.tableWidget_Project.keyList:
#             temp_sql = """INSERT INTO t_archives_project 
#                         (archives_pk, project_pk) 
#                         VALUES (@archives_pk,{});"""
#             result.append(temp_sql.format(pk))
#         return result

#     # 附件保存按钮
#     def CopyPicAndGetSaveFileSQL(self) -> list:
#         sqls = []
#         used_sql = """
#                 select archives_pk from t_additionals_archives
#                 where file_pk={file_pk} 
#                     and archives_pk<>{archives_pk} limit 1;
#                 """
#         del_sql = """
#                 delete from t_additionals_archives
#                 where archives_pk={archives_pk} 
#                     and file_pk={file_pk};
#                 """
#         ins_file = """
#                 insert into t_additionals
#                     (original_name,filemd5,file_type)
#                     Values ('{original_name}',
#                     unhex('{filemd5}'),'{file_type}');
#                 """
#         ins_add = """
#                 insert into t_additionals_archives
#                     (archives_pk,file_pk,file_index)
#                     Values ({archives_pk},{file_pk},{file_index});
#                 """
#         up_index = """update t_additionals_archives
#                         set file_index={file_index}
#                         where archives_pk={archives_pk}
#                             and file_pk={file_pk}"""
#         temp_id = self.ui.archives_pk.text()
#         cur_pk = temp_id.replace(",", "") if self.isEditMode else ''
#         if self.isNewMode:

#             cur_pk = '@archives_pk'

#         def fileIsUsed(file_pk, archives_pk):
#             s = used_sql.format(file_pk=file_pk, archives_pk=archives_pk)
#             return JPDb().executeTransaction(s)
#         # self.setCursor(Qt.WaitCursor)
#         for iRow, r in enumerate(self.addtionalInfo):
#             # 删除情况1：用户删除了一个数据库已经存在的文件
#             if r["archives_pk"] and r["deleted"]:
#                 # 删除本附件对文件的引用
#                 tempsql = del_sql.format(
#                     file_pk=r["file_pk"], archives_pk=r["archives_pk"])
#                 sqls.append(tempsql)
#                 if fileIsUsed(r["file_pk"], r["archives_pk"]):
#                     # 如果文件已经被其他附件引用，则只删除本附件的引用
#                     continue
#                 else:
#                     # 如果没有没有被其他用户引用，物理删除之
#                     filePath = r["file_name"]
#                     if os.path.exists(filePath):
#                         self.ui.Label_Info.setText(
#                             "正在删除【{}】".format(filePath))
#                         os.remove(filePath)
#                         self.self.ui.Label_Info.setText('')
#             # 删除情况2：如果是刚刚增加的文件被用户删除，则跳过不处理本行数据
#             if not r["archives_pk"] and r["deleted"]:
#                 continue

#             # 增加情况1：增加的文件数据库中已经有其他附件引用
#             if r["alreadyExist"] and not r["deleted"]:
#                 p_s = ins_add.format(
#                     archives_pk=cur_pk,
#                     file_pk=r["alreadyExist"],
#                     file_index=iRow)
#                 sqls.append(p_s)
#             # 增加情况2：增加的文件数据库中不存在，进行物理复制
#             if not r["alreadyExist"] and not r["archives_pk"]:
#                 p_s = "{con_path}/{filemd5}.{file_type}"
#                 newPath = p_s.format(
#                     con_path=self.con_path,
#                     filemd5=r["filemd5"],
#                     file_type=r["file_type"])
#                 self.ui.Label_Info.setText(
#                     "正在复制【{}】".format(r["original_path"]))
#                 myCopy(r["original_path"], newPath)
#                 self.ui.Label_Info.setText('')
#                 # 先增加一个文件，后面要用到自动生成的文件PK
#                 tempsql = ins_file.format(
#                     original_name=r["original_name"],
#                     filemd5=r["filemd5"],
#                     file_type=r["file_type"])
#                 sqls.append(tempsql)
#                 tempsql = ins_add.format(
#                     archives_pk=cur_pk,
#                     file_pk='({})'.format(JPDb().LAST_INSERT_ID_SQL()),
#                     file_index=iRow)
#                 sqls.append(tempsql)

#             # 如果没有删除并且是一个已经存在的文件，修改显示顺序
#             if r["archives_pk"] and not r["deleted"]:
#                 tempsql = up_index.format(
#                     archives_pk=cur_pk,
#                     file_pk=r['file_pk'],
#                     file_index=iRow)
#                 sqls.append(tempsql)
#         # self.setCursor(Qt.ArrowCursor)
#         return sqls
#         # JPDb().executeTransaction(sqls)
