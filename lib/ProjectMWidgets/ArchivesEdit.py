

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
from lib.JPPublc import JPDb, JPPub, JPUser, FormPopProgressBar
from lib.JPMvc.JPEditFormModel import JPEditFormDataMode, JPFormModelMain
from lib.JPFunction import JPDateConver
from lib.JPDatabase.Query import JPTabelFieldInfo
from lib.JPExcel.JPExportToExcel import JPExpExcelFromTabelFieldInfo
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog, QTableWidgetItem, QItemDelegate,
                             QDialog, QLabel, QScrollArea, QVBoxLayout,
                             QAction, QMenu, QListWidgetItem, QListWidget,
                             QDesktopWidget, QAbstractItemView, QListView)
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QGuiApplication, QCursor)
import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())


class addtionalInfo():
    def __init__(self):
        '''存放一个附件数据的类'''
        super().__init__()
        self.additional_pk = None
        self.archives_pk = None
        self.file_index = None
        self.file_type = None
        self.file_pk = None
        self.original_name = None
        self.original_path = None
        self.file_name = None
        self.deleted = None
        self.alreadyExist = None
        self.alreadyDisplayed = None


class picInfo():
    def __init__(self):
        super().__init__()
        self.Md5Fileindex = 0
        self.viewPicPath = ''
        self.pageIndex = 0
        self.originalName = ''
        self.iconPath = False
        self.originalPath = ''

    def __str__(self):
        s = """Type: picInfo
                Md5Fileindex={},
                viewPicPath='{}',
                pageIndex={},
                originalName='{}',
                iconPath={},
                originalPath='{}'"""
        s = s.format(
            self.Md5Fileindex,
            self.viewPicPath,
            self.pageIndex,
            self.originalName,
            self.iconPath,
            self.originalPath
        )
        return s


class Form_ViewPic(QDialog):
    def __init__(self, parent=None,
                 vPicInfo=None,
                 linkList=None,
                 flags=Qt.WindowFlags()):
        pub = JPPub()
        super().__init__(parent=pub.MainForm, flags=flags)
        self.ui = Ui_Dialog_ViewPic()
        self.ui.setupUi(self)
        self.currentPicInfo = vPicInfo
        self.linkList = linkList
        self.ui.label.setScaledContents(False)
        self.setModal(True)
        self.showMaximized()
        self.dispCurrentPic()


    def dispCurrentPic(self):
        """给窗体设置要显示的图片信息及链表"""
        p = self.currentPicInfo.viewPicPath
        self.ui.label.setPixmap(QPixmap(p).scaledToHeight(
            self.ui.label.height(), Qt.SmoothTransformation))
        self.setButHide()

    def resizeEvent(self, resizeEvent):
        if self.currentPicInfo:
            self.dispCurrentPic()


    def setButHide(self):
        # 在链表中找当前信息
        cur_Node = self.linkList.findNode(self.currentPicInfo)
        self.CurrentNode = cur_Node
        self.ui.butFirst.setEnabled(cur_Node.prev is not None)
        self.ui.butPre.setEnabled(cur_Node.prev is not None)
        self.ui.butNext.setEnabled(cur_Node.next is not None)
        self.ui.butLast.setEnabled(cur_Node.next is not None)

    @pyqtSlot()
    def on_butFirst_clicked(self):
        self.currentPicInfo = self.linkList._head.item
        self.dispCurrentPic()

    @pyqtSlot()
    def on_butPre_clicked(self):
        self.currentPicInfo = self.CurrentNode.prev.item
        self.dispCurrentPic()

    @pyqtSlot()
    def on_butNext_clicked(self):
        self.currentPicInfo = self.CurrentNode.next.item
        self.dispCurrentPic()

    @pyqtSlot()
    def on_butLast_clicked(self):
        self.currentPicInfo = self.linkList.lastNode.item
        self.dispCurrentPic()


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



class MyThreadReadAddition(QThread):
    """加载附件图片的线程类, 每生成一个对象，都通过信号把数据发出
    本线程只负责从已经加载完成的数据字典中的一行生成图片对象
    图片的集合应由主界面维护
    """
    onePixmCreated = pyqtSignal(picInfo)
    oneFileLoaded = pyqtSignal(str)

    def __init__(self, addtionalData):
        super().__init__()
        self.cachePath = os.path.join(os.getcwd(), "cache")
        if not os.path.exists(self.cachePath):
            os.mkdir(self.cachePath)
        self.addtionalData = addtionalData
        self.defHeight = 200
        self.pub = JPPub()

    def render_pdf_page(self, page_data, rowAddtionalData, i):
        imageFormat = QImage.Format_RGB888
        pagePixmap1 = page_data.getPixmap(
            matrix=fitz.Matrix(1, 1),
            alpha=False)
        pageQImage1 = QImage(
            pagePixmap1.samples,
            pagePixmap1.width,
            pagePixmap1.height,
            pagePixmap1.stride,
            imageFormat)
        # 生成 pixmap 对象
        pixmap1 = QPixmap()
        pixmap1.convertFromImage(pageQImage1)
        fn = os.path.join(self.cachePath, "{}_{}.jpg".format(
            GetStrAsMD5(rowAddtionalData.file_name), i))
        pixmap1.save(fn, "JPG")
        temp = picInfo()
        temp.Md5FileIndex = rowAddtionalData.file_index
        temp.pageIndex = i
        temp.originalName = rowAddtionalData.original_name
        temp.viewPicPath = fn
        return temp

    def createEveryPixmapFromFile(self):
        for i, r in enumerate(self.addtionalData):
            if r.deleted:
                continue
            #################################
            # 找到要显示文件的真实路径（数据库中已经存在的和新添加的不同，alreadyExist用于防止用户重复添加同一文件）
            filePath = r.file_name if (
                r.alreadyExist or r.archives_pk) \
                else r.original_path
            if os.path.exists(filePath):
                expName = r.file_type.upper()
                docDic = {"XLS": 0, "XLSX": 0, "DOC": 1,
                          "DOCX": 1, "ZIP": 2, "RAR": 3}
                icoLst = ["excel.png", "word.png",
                          "zip.png", "rar.png"]
                if expName in docDic.keys():
                    pi = picInfo()
                    icoName = icoLst[docDic[expName]]
                    pi.iconPath = self.pub.getIcoPath(icoName)
                    pi.originalPath = filePath
                    self.onePixmCreated.emit(pi)
                    # readIco(icoLst[docDic[expName]], r, filePath)
                elif expName in ["JPG", "PNG", "BMP"]:
                    pi = picInfo()
                    pi.originalPath = filePath
                    pi.viewPicPath = filePath
                    self.onePixmCreated.emit(pi)
                    #readPIC(filePath, r)
                elif expName == "PDF":
                    doc = fitz.open(filePath)
                    for i in range(doc.pageCount):
                        pageData = doc.loadPage(i)
                        pi = self.render_pdf_page(
                            pageData, r, i)
                        self.onePixmCreated.emit(pi)
                    doc.close()
            else:
                logging.getLogger().error("文件没有找到:{}".format(filePath))
            self.oneFileLoaded.emit(r.original_name)

    def run(self):
        self.createEveryPixmapFromFile()


class EditForm_Archive(JPFormModelMain):
    currentRowEditComplete = pyqtSignal(int)

    def __init__(self, sql_main, PKValue, edit_mode, flags=Qt.WindowFlags()):
        super().__init__(Ui_Form_Edit(),
                         sql_main=sql_main,
                         PKValue=PKValue,
                         edit_mode=edit_mode,
                         flags=flags)
        self.MainForm = JPPub().MainForm
        self.MainForm.addLogoToLabel(self.ui.label_logo)
        self.MainForm.addOneButtonIcon(self.ui.butSave, 'save.png')
        self.MainForm.addOneButtonIcon(self.ui.butCancel, 'cancel.png')

        #　设置listWidget的格式
        self.ui.listWidget.setGridSize(QSize(210, 279))
        self.ui.listWidget.setResizeMode(QListWidget.Adjust)
        self.ui.listWidget.setIconSize(QSize(210, 279))
        # self.ui.listWidget.setFlow(QListView.LeftToRight)
        # self.ui.listWidget.setSelectionModel(QAbstractItemView.SingleSelection)
        self.ui.listWidget.setSpacing(10)
        self.ui.listWidget.itemDoubleClicked.connect(
            self.listItemDoubleClicked)
        self.ui.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listWidget.customContextMenuRequested.connect(self.rightClicked)
        # 标签文本自动换行
        self.ui.label_ProjectLink.setWordWrap(True)
        self._currentEditModelRow = None
        self.ui.fUserID.hide()
        self.pop = FormPopProgressBar(self)
        # 存放用户已经选择的关联项目
        self.keyList = []
        # addtionalInfo用来以文件为行，保存档案的附件数据，用于保存命令等
        self.addtionalInfo = []
        # listIcos是一个列表，内部存放所有在listWidget中显示的图标
        self.listIcos = []
        # 下面的链表，用于存放listIcos中可用于放大显示的图片
        self.viewPicInfos = BilateralLinkList()
        # # 一个只包含PDF页面和图片的列表,由编辑窗体维护，用于放大显示时用
        # self.ViewPdfAndPic = []
        self.archivesPathInDatabase = JPPub().getConfigData()["archives_path"]
        if self.isNewMode:
            self.ui.fUserID.setText(str(JPUser().currentUserID()))
        self.readData()
        if (not self.isNewMode) and self.ui.archives_pk.text():
            sql = "select project_pk from "
            sql = sql + "t_archives_project where archives_pk={}"
            dic = JPDb().getDict(sql.format(
                self.ui.archives_pk.text().replace(",", "")))
            projects = [str(r['project_pk']) for r in dic]
            if projects:
                self.readProject(projects)

        self.ui.archives_pk.setEnabled(False)
        self.ui.issuing_date.setFocus()
        # QGuiApplication.processEvents()
        # self.repaint()
        self.readAddtionalFromDatabase()
        self.initAdditional()

        # 根据窗体编辑状态设置窗体中按钮的显示状态
        if self.isReadOnlyMode:
            self.ui.but_SelectProject.setEnabled(False)
            # self.ui.btn_Download.setEnabled(False)
            self.ui.btn_Add.setEnabled(False)
            self.ui.btn_Delete.setEnabled(False)

    def closeEvent(self, event):
        import gc
        del self.addtionalInfo
        gc.collect()
        event.accept()

    def initAdditional(self):
        if self.addtionalInfo:
            self.xc = MyThreadReadAddition(self.addtionalInfo)
            self.xc.onePixmCreated.connect(self.addOnePixmaptoForm)
            self.xc.oneFileLoaded.connect(self.pop.dispInfoStep)
            self.pop.open()
            self.pop.setMaximum(len(self.addtionalInfo))
            self.xc.start()

    def rightClicked(self,point):
        popMenu = QMenu()
        popMenu.addAction(QAction(u'添加', self))
        popMenu.addAction(QAction(u'删除', self))
        popMenu.addAction(QAction(u'修改', self))
        ac=popMenu.exec_(QCursor.pos())
        if ac:
            print(ac)
    def deleteAddtional(self, fileanme: str):
        Labels = self.findChildren(
            QLabel, "loadPic", Qt.FindChildrenRecursively)
        delLabels = [item for item in Labels if
                     item.addtionalData["original_name"] == fileanme]
        for item in delLabels:
            for r in reversed(self.ViewPdfAndPic):
                if r['addtionalData'] is item.addtionalData:
                    self.ViewPdfAndPic.remove(r)
            item.hide()

        lst2 = [item for item in self.addtionalInfo
                if item["original_name"] == fileanme]
        for item in lst2:
            item["deleted"] = True

    def listItemDoubleClicked(self, item):
        frm = Form_ViewPic(self, item.picInfo, self.viewPicInfos)
        # frm.setData(item.picInfo, self.viewPicInfos)
        frm.show
        print(item.picInfo)
        return

    def addOnePixmaptoForm(self, item: picInfo):
        obj = None
        if not item.iconPath:
            self.viewPicInfos.append(item)
            obj = QPixmap(item.viewPicPath)
        else:
            obj = QPixmap(item.iconPath)
        # 生成一个列表项
        pItem = QListWidgetItem(QIcon(obj.scaled(
            QSize(210, 279), Qt.KeepAspectRatio,
            Qt.SmoothTransformation)), '')
        pItem.setSizeHint(QSize(210, 279))
        pItem.picInfo = item
        pItem.setToolTip(item.originalName)
        self.ui.listWidget.addItem(pItem)
        QGuiApplication.processEvents()
        # 将该picInfo加入到列表及链表
        self.listIcos.append(item)


    def onGetFieldsRowSources(self):
        pub = JPPub()
        return [
            ('archive_type', pub.getEnumList(5), 1)
        ]

    def readProject(self, pklst):
        self.keyList = pklst
        sql = """
            SELECT group_concat(project_pk) as pks,
                group_concat(project_simple_name) as nms
            FROM t_project_base_info
            WHERE project_pk IN ({})
            """
        sql = sql.format(','.join(pklst))
        data = JPDb().getDataList(sql)
        self.ui.label_ProjectLink.setText(data[0][1])

        return

    def readAddtionalFromDatabase(self):
        """从数据库中加载给定PK的一个文档的所有附件信息到一个列表中"""
        sql = """
        select additional_pk,
            archives_pk,
            file_index,
            file_type,
            file_pk,
            original_name,
            '' as original_path,
            concat('{}/',file_name) as file_name,
            False as deleted,
            0 as alreadyExist,
            0 as alreadyDusplayed
        from v_additional_archives
        where archives_pk={}
        order by file_index
        """
        if not self.isNewMode:
            #　从数据库取数据，生成多个addtionalInfo对象
            pk = self.ui.archives_pk.text().replace(",", "")
            d_path = self.archivesPathInDatabase
            dic = JPDb().getDict(sql.format(d_path, pk))
            for r in dic:
                add = addtionalInfo()
                for k, v in r.items():
                    add.__dict__[k] = v
                self.addtionalInfo.append(add)

    # def resizeEvent(self, QResizeEvent):
    #     print("resize")
    #     return super().resizeEvent(QResizeEvent)

    def onFirstHasDirty(self):
        self.ui.butSave.setEnabled(True)

    @pyqtSlot()
    def on_butCancel_clicked(self):
        self.close()

    @pyqtSlot()
    # 已经调试 增加一个附件
    def on_btn_Add_clicked(self):
        def getExName(filepath):
            t = filepath.split(".")
            return t[len(t)-1]

        def md5Exist(filepath: str):
            """检查文件是否在数据库中已经存在"""
            sql = """select file_Pk,
                        concat('{}/',file_name) as file_name,
                        file_type
                    from v_additional_archives
                    where filemd5=unhex('{}') limit 1;"""
            md5BaseName = GetFileMd5(filepath)
            md5FileName = '.'.join((md5BaseName, getExName(filepath)))
            lst = JPDb().getDataList(sql.format(self.archivesPathInDatabase, md5BaseName))
            exist = True if lst else False
            return exist, md5FileName, md5BaseName, lst if exist else None
        fileName_choose, filetype = QFileDialog.getOpenFileNames(
            self,
            "Select a File",
            JPPub().getOrSetlastOpenDir(),  # 起始路径
            "Files (*.jpg *.PDF *.doc *.docx *.xls *.xlsx)")
        if fileName_choose:
            JPPub().getOrSetlastOpenDir(fileName_choose[0])
        for i, original_path in enumerate(fileName_choose):
            self.ui.archive_describe.append(os.path.basename(original_path))
            self.pop.dispInfo(original_path, i)
            dicrow = {'additional_pk': None,
                      'archives_pk': None,
                      'file_index': 0,
                      'original_name': '',
                      'original_path': '',
                      'file_type': '',
                      'file_name': '',
                      'deleted': 0,
                      'alreadyExist': 0,
                      'filemd5': ''}
            # 检查文件是不是刚刚在窗体中增加过一次
            upLoadFile = [r['original_path']
                          for r in self.addtionalInfo if not r['archives_pk']]
            if original_path in upLoadFile:
                self.ui.Label_Info.setText(
                    "文件【{}】刚刚已经增加".format(original_path))
                continue
            # 检查要上传的文件在数据库中是不是已经存在
            exist, md5FileName, md5BaseName, lst = md5Exist(original_path)
            if exist:
                dicrow["alreadyExist"] = lst[0][0]
                dicrow["file_name"] = lst[0][1]
                dicrow["file_type"] = lst[0][2]
                dispTxt = "【{}】文件在数据库中存在，已经用数据库中文件替代显示！"
                self.ui.Label_Info.setText(
                    dispTxt.format(os.path.basename(original_path)))
            else:
                dicrow["filemd5"] = md5BaseName
                dicrow["file_type"] = getExName(md5FileName)
                dicrow["file_name"] = os.path.join(
                    self.archivesPathInDatabase, md5FileName)
                dicrow["original_path"] = original_path
                dicrow["original_name"] = os.path.basename(original_path)

            self.addtionalInfo.append(dicrow)
            self.initAdditional()
            self.firstHasDirty.emit()

    @pyqtSlot()
    # 已经调试
    def on_but_SelectProject_clicked(self):
        rows = self.ui.tableWidget_Project.rowCount()
        sels = [self.ui.tableWidget_Project.item(
            i, 0).text() for i in range(rows)]
        frm = FormSelectProject(sels)
        frm.selectItemChanged.connect(self.readProject)
        frm.show()
        self.firstHasDirty.emit()

    @pyqtSlot()
    # 已经调试
    def on_btn_Download_clicked(self):
        # self.setCursor(Qt.WaitCursor)
        tm = time.strftime('%Y%m%d%H%M%S', time.localtime())
        uid = JPUser().currentUserID()
        initPath = "{}_{}".format(uid, tm)
        temppath = os.getcwd()+"/temp"
        topath = os.path.join(temppath, initPath)
        if not os.path.exists(topath):
            os.makedirs(topath)
        lst = [item for item in self.addtionalInfo if not item['deleted']]
        copylst = []
        for i, item in enumerate(lst):
            if item['archives_pk']:
                fr = os.path.join(
                    self.archivesPathInDatabase, item["file_name"])
                to = os.path.join(topath, item["original_name"])
                copylst.append([fr, to])
            else:
                fr = item["original_path"]
                to = os.path.join(topath, item["original_name"])
                copylst.append([fr, to])
        pop = FormPopProgressBar(self)
        pop.showInfo(len(copylst)-1)
        for r in copylst:
            pop.dispInfo("复制{}".format(r[1]), i)
            myCopy(r[0], r[1])
        pop.close()
        txt = '文件保存在：【{}】,点击确定打开该文件夹！'.format(topath)
        if QMessageBox.question(self,
                                '完成',
                                txt,
                                (QMessageBox.Yes | QMessageBox.No),
                                QMessageBox.Yes) == QMessageBox.Yes:
            topath1 = os.path.abspath(topath)
            os.system("start explorer {}".format(topath1))

        # self.setCursor(Qt.ArrowCursor)

    @pyqtSlot()
    def on_butSave_clicked(self):
        try:
            s1 = self.getSqls(self.PKRole)
        except Exception as e:
            t = '生成保存档案数据SQL命令出错，错误信息：\n{}'
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', t.format(str(e)))
            msgBox.exec_()
            return

        try:
            s2 = self.CopyPicAndGetSaveFileSQL()
        except Exception as e:
            t = '复制文件或生成保存文件数据SQL命令出错，错误信息：\n{}'
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', t.format(str(e)))
            msgBox.exec_()
            return
        pkSQL = []
        if self.isNewMode:
            sPK = JPDb().LAST_INSERT_ID_SQL()
            pkSQL.append("{} into @archives_pk;".format(sPK))
        if self.isEditMode:
            cur_pk = self.ui.archives_pk.text().replace(",", "")
            pkSQL.append('Select {} into @archives_pk;'.format(cur_pk))
        # 更新关联项目的SQL
        up_projectSQL = self. getUpdateProjectSQL()
        # 拼接所有SQL
        SQLS = s1[0:len(s1)-1] + pkSQL + up_projectSQL + s2
        SQLS.append("Select @archives_pk;")

        # 执行sql
        try:
            isOK, result = JPDb().executeTransaction(SQLS)
            if isOK:
                self.ui.butSave.setEnabled(False)
                self.afterSaveData.emit(result)
                self.currentRowEditComplete.emit(self._currentEditModelRow)
                QMessageBox.information(self, '完成',
                                        '保存数据完成！\nSave data complete!')
        except Exception as e:
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', str(e))
            msgBox.exec_()
        finally:
            self.close()

    def getUpdateProjectSQL(self):
        result = []
        if self.isEditMode:
            delSQL = """delete from t_archives_project
                        where archives_pk=@archives_pk;"""
            result.append(delSQL)
        for pk in self.ui.textEditLinkProject:
            temp_sql = """INSERT INTO t_archives_project
                        (archives_pk, project_pk)
                        VALUES (@archives_pk,{});"""
            result.append(temp_sql.format(pk))
        return result

    # 附件保存按钮
    def CopyPicAndGetSaveFileSQL(self) -> list:
        sqls = []
        used_sql = """
                select archives_pk from t_additionals_archives
                where file_pk={file_pk}
                    and archives_pk<>{archives_pk} limit 1;
                """
        del_sql = """
                delete from t_additionals_archives
                where archives_pk={archives_pk}
                    and file_pk={file_pk};
                """
        ins_file = """
                insert into t_additionals
                    (original_name,filemd5,file_type)
                    Values ('{original_name}',
                    unhex('{filemd5}'),'{file_type}');
                """
        ins_add = """
                insert into t_additionals_archives
                    (archives_pk,file_pk,file_index)
                    Values ({archives_pk},{file_pk},{file_index});
                """
        up_index = """update t_additionals_archives
                        set file_index={file_index}
                        where archives_pk={archives_pk}
                            and file_pk={file_pk}"""
        temp_id = self.ui.archives_pk.text()
        cur_pk = temp_id.replace(",", "") if self.isEditMode else ''
        if self.isNewMode:

            cur_pk = '@archives_pk'

        def fileIsUsed(file_pk, archives_pk):
            s = used_sql.format(file_pk=file_pk, archives_pk=archives_pk)
            return JPDb().executeTransaction(s)
        # self.setCursor(Qt.WaitCursor)
        for iRow, r in enumerate(self.addtionalInfo):
            # 删除情况1：用户删除了一个数据库已经存在的文件
            if r["archives_pk"] and r["deleted"]:
                # 删除本附件对文件的引用
                tempsql = del_sql.format(
                    file_pk=r["file_pk"], archives_pk=r["archives_pk"])
                sqls.append(tempsql)
                if fileIsUsed(r["file_pk"], r["archives_pk"]):
                    # 如果文件已经被其他附件引用，则只删除本附件的引用
                    continue
                else:
                    # 如果没有没有被其他用户引用，物理删除之
                    filePath = r["file_name"]
                    if os.path.exists(filePath):
                        self.ui.Label_Info.setText(
                            "正在删除【{}】".format(filePath))
                        os.remove(filePath)
                        self.self.ui.Label_Info.setText('')
            # 删除情况2：如果是刚刚增加的文件被用户删除，则跳过不处理本行数据
            if not r["archives_pk"] and r["deleted"]:
                continue

            # 增加情况1：增加的文件数据库中已经有其他附件引用
            if r["alreadyExist"] and not r["deleted"]:
                p_s = ins_add.format(
                    archives_pk=cur_pk,
                    file_pk=r["alreadyExist"],
                    file_index=iRow)
                sqls.append(p_s)
            # 增加情况2：增加的文件数据库中不存在，进行物理复制
            if not r["alreadyExist"] and not r["archives_pk"]:
                p_s = "{con_path}/{filemd5}.{file_type}"
                newPath = p_s.format(
                    con_path=self.archivesPathInDatabase,
                    filemd5=r["filemd5"],
                    file_type=r["file_type"])
                self.ui.Label_Info.setText(
                    "正在复制【{}】".format(r["original_path"]))
                myCopy(r["original_path"], newPath)
                self.ui.Label_Info.setText('')
                # 先增加一个文件，后面要用到自动生成的文件PK
                tempsql = ins_file.format(
                    original_name=r["original_name"],
                    filemd5=r["filemd5"],
                    file_type=r["file_type"])
                sqls.append(tempsql)
                tempsql = ins_add.format(
                    archives_pk=cur_pk,
                    file_pk='({})'.format(JPDb().LAST_INSERT_ID_SQL()),
                    file_index=iRow)
                sqls.append(tempsql)

            # 如果没有删除并且是一个已经存在的文件，修改显示顺序
            if r["archives_pk"] and not r["deleted"]:
                tempsql = up_index.format(
                    archives_pk=cur_pk,
                    file_pk=r['file_pk'],
                    file_index=iRow)
                sqls.append(tempsql)
        # self.setCursor(Qt.ArrowCursor)
        return sqls
        # JPDb().executeTransaction(sqls)
