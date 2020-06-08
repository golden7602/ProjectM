import logging
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QGuiApplication, QCursor)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QMetaObject, pyqtSlot, Qt, QModelIndex
import re
from PyQt5.QtWidgets import (QMessageBox, QPushButton, QWidget, QLineEdit,
                             QFileDialog)
from lib.JPFunction import GetFileMd5
from lib.JPPublc import JPDb, JPPub, JPUser
from Ui.Ui_FormToolsImport import Ui_Form as Ui_Form_Tools
from PIL import Image as PLIImage
from pathlib import Path
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
from sys import path as jppath
from shutil import copyfile as myCopy
jppath.append(os.getcwd())


def getExName(filepath):
    t = filepath.split(".")
    return t[len(t)-1]


def md5Exist(filepath: str, con_path):
    """检查文件是否在数据库中已经存在"""
    sql = """select file_Pk
            from t_additionals
            where filemd5=unhex('{}') limit 1;"""
    md5BaseName = GetFileMd5(filepath)
    md5FileName = '.'.join((md5BaseName, getExName(filepath)))
    sql = sql.format(md5BaseName)
    sql = sql.replace('\n', '')
    isOK, pk = JPDb().executeTransaction(sql)
    exist = True if pk else False
    file_pk = pk
    return exist, md5FileName, md5BaseName, file_pk


def sqm(text: str) -> str:
    """给字符串加上单引号"""
    return "'{}'".format(text)


class FileToolsImport(QtWidgets.QDialog):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        pub = JPPub()
        super().__init__(parent=pub.MainForm, flags=flags)
        self.setWindowTitle("工具集")
        self.ui = Ui_Form_Tools()
        self.ui.setupUi(self)
        self.addtionalInfo = []
        self.MainForm = pub.MainForm
        self.ui.label_import.setPixmap(self.MainForm.getPixmap('import.png'))
        # self.ui.label_pdf.setPixmap(self.MainForm.getPixmap('file_pdf.png'))
        self.initComboFileType()
        self.ui.comboBox_FileType.currentIndexChanged[str].connect(
            self.onComboFileFypeChanged)
        self.con_path = JPPub().getConfigData()["archives_path"]
        self.ui.pb.setRange(0, 0)
        self.ui.pb.hide()
        self.ui.label_info.hide()
        self.exec_()

    def onComboFileFypeChanged(self, s):
        lst = s.split(",")
        self.archive_type = lst[0]

    def getFieldsValues(self, txt: str):
        """返回一个文件名或文件夹名中的字段信息"""
        result = {}
        result['issuing_date'] = None
        result['archive_no'] = None
        result['key_words'] = None
        result['base_name'] = None
        result['ex_name'] = None
        result['archive_type'] = None
        result['archive_describe'] = None
        result['title'] = None
        ZiHaoFound = False
        fileYear = ''
        archive_type = {
            "党工委专项会议纪要": 32,
            "董事会(董联会)纪要": 45,
            "督办单": 29,
            "工作联系函": 30,
            "管委会文件": 34,
            "管委会专题会议纪要": 31,
            "高新区管委会专项问题会议纪要": 31,
            "管委会专项会议纪要": 31,
            '管委会专项问题会议纪要': 31,
            "集团党委会议纪要": 44,
            "集团党委文件": 37,
            "集团党委专题会议纪要": 35,
            "集团专题会议纪要": 36,
            "集团总经理办公会文件": 38,
            '总经理办公会议纪要': 38,
            '总办会议纪要': 38,
            "批量导入未修改": 43,
            "其他外部单位来文": 42,
            "通知或函": 41,
            "文件批办单": 39,
            "项目手续文件-立项": 46,
            "主任办公会会议纪要": 40,
            "集团党委会会议纪要": 44,
            "董事会会议纪要": 45,
            '董事长联席会议纪要': 45,
            "董联会会议纪要": 45,
            "董事长联席会议纪要": 45,
            "集团党委专题会会议纪要": 35,
            "项目立项文件": 46,
            "下达追加目标考核任务目标通知书": 49,
            "下达追加考核任务通知书": 49,
            "下达追加目标考核任务目标通知书": 49
        }
        for k, v in archive_type.items():
            if k in txt:
                result['archive_type'] = sqm(v)
                break
        # 取文件或路径基本名，用于后面的处理
        if os.path.isfile(txt):
            p_basename = r'(.*)\.(.{3,4})'
            filename = os.path.basename(txt)
            filename = filename.replace("+", " ").replace("  ", " ")
            mat = re.search(p_basename, filename)
            result['base_name'] = sqm(mat.groups()[0].strip())
            result['archive_describe'] = sqm(result['base_name'])
            result['ex_name'] = sqm(mat.groups()[1].strip())
            txt = mat.groups()[0].strip()
        if os.path.isdir(txt):
            ls = str.split(txt, "/")
            txt = ls[len(ls)-1]
            txt = txt.replace("+", " ").replace("  ", " ")
            result['base_name'] = sqm(txt)
        noKeyNodate = ''
        noKeys = ''
        # 取关键字
        p_keywords = r"([（|\(]关键字[：|:](.*)[）|\)])"
        mat = re.search(p_keywords, txt)
        if mat:
            result['key_words'] = sqm(mat.groups()[1].strip())
            a1, a2 = mat.regs[0]
            txt = (txt[0:a1]+txt[(a2+1):]).strip()
            noKeys = (txt[0:a1]+txt[(a2+1):]).strip()
        # 取日期
        p_Wenjianriqi = r"(\d{4}).(\d{1,2}).(\d{1,2})"
        mat = re.search(p_Wenjianriqi, txt)
        if mat:
            fileYear = "{}年".format(mat.groups()[0])
            result['issuing_date'] = sqm("-".join(mat.groups()))
            a1, a2 = mat.regs[0]
            txt = (txt[0:a1]+txt[(a2+1):]).strip()
            noKeyNodate = (txt[0:a1]+txt[(a2+1):]).strip()
        # 取文件字号
        if not ZiHaoFound:
            p_WenJianZiHao = r'([\u4e00-\u9fa5]*[字发函]\s?[\(\[【〔]\d{4}[\)\]）〕】]\d{1,4}号)'
            mat = re.search(p_WenJianZiHao, txt)
            if mat:
                temp_zh = txt[mat.regs[0][0]:mat.regs[0][1]+1]
                if temp_zh[len(temp_zh)-1] == '）':
                    temp_zh = temp_zh[0:len(temp_zh)-2]
                temp_zh = temp_zh.replace("【", "〔")
                temp_zh = temp_zh.replace("】", "〕")
                temp_zh = temp_zh.replace("[", "〔")
                temp_zh = temp_zh.replace("]", "〕")
                result['archive_no'] = sqm(temp_zh)
                a1, a2 = mat.regs[0]
                txt = (txt[0:a1]+txt[(a2+1):]).strip()
                ZiHaoFound = True
        if not ZiHaoFound:
            p_WenJianZiHao = r'（(第\d{1,3}期)）.*$'
            mat = re.search(p_WenJianZiHao, txt)
            if mat:
                result['archive_no'] = sqm(fileYear + mat.groups()[0].strip())
                a1, a2 = mat.regs[0]
                txt = (txt[0:a1]+txt[(a2+1):]).strip()
                ZiHaoFound = True
        if not ZiHaoFound:
            p_WenJianZiHao = r'总经理办公会议纪要（(\d{1,3})）'
            mat = re.search(p_WenJianZiHao, txt)
            if mat:
                result['archive_no'] = sqm(
                    fileYear + "第"+mat.groups()[0].strip()+"期")
                a1, a2 = mat.regs[0]
                txt = (txt[0:a1]+txt[(a2+1):]).strip()
                result['title'] = sqm(noKeyNodate)
                ZiHaoFound = True
        if not ZiHaoFound:
            p_WenJianZiHao = r'第(\d{1,3})次总经理办公会议纪要'
            mat = re.search(p_WenJianZiHao, txt)
            if mat:
                result['archive_no'] = sqm(
                    fileYear + "第"+mat.groups()[0].strip()+"期")
                a1, a2 = mat.regs[0]
                txt = (txt[0:a1]+txt[(a2+1):]).strip()
                result['title'] = sqm(noKeyNodate)
                ZiHaoFound = True
        if not result['title']:
            result['title'] = sqm(txt) if txt else noKeys
        return result

    def initComboFileType(self):
        lst = JPPub().getEnumList(5)
        combo = self.ui.comboBox_FileType
        for r in lst:
            combo.addItem('{},{}'.format(r[1], r[0]))
        for i, r in enumerate(lst):
            if r[1] == 43:
                combo.setCurrentIndex(i)
                self.archive_type = 43
                break

    def showInfo(self, range):
        self.ui.pb.show()
        self.ui.pb.setRange(0, range)
        self.ui.label_info.show()
        self.ui.textBrowser.clear()
        self.ui.label_info.setText("")

    def dispInfo(self, text, value):
        self.ui.label_info.setText(text)
        self.ui.pb.setValue(value)
        self.ui.textBrowser.append(text)
        QGuiApplication.processEvents()

    def hideInfo(self):
        self.ui.pb.hide()
        self.ui.pb.hide()
        self.ui.pb.setRange(0, 0)
        self.ui.textBrowser.clear()
        self.ui.label_info.setText("")

    def getInsertArchiveSQL(self, archive_type, values):
        """生成插入档案SQL"""
        archive_type = str(archive_type)
        flds = ['fUserID']
        vals = [sqm(JPUser().currentUserID())]
        lst = ['issuing_date',
               'archive_no',
               'key_words',
               'title',
               'archive_describe',
               'archive_type']
        for k in lst:
            if values[k]:
                flds.append(k)
                vals.append(values[k])
        strFld, strVal = ",".join(flds), ",".join(vals)
        s = "INSERT INTO t_archives ({}) VALUES ({});"
        return s.format(strFld, strVal)

    def getAndCheckPaths(self) -> list:
        QF = QFileDialog.getExistingDirectory
        fns = QF(self, "选择文件夹", JPPub().getOrSetlastOpenDir())
        if not fns:
            return []
        JPPub().getOrSetlastOpenDir(fns)
        result = os.listdir(fns)
        err_file = []
        err_path = []
        r_path = []
        self.showInfo(len(result))
        for i, p in enumerate(result):
            fullPath = '/'.join((fns, p))
            s = "检查[{}]".format(fullPath)
            logging.getLogger().debug(s)
            self.dispInfo(s, i)
            QGuiApplication.processEvents()
            if os.path.isfile(fullPath):
                s = "[{}]是一个文件，不能导入".format(p)
                logging.getLogger().warning(s)
                err_file.append(s)
                continue
            if os.path.isdir(fullPath):
                subPath = os.listdir(fullPath)
                for sub in subPath:
                    sub_full = '/'.join((fullPath, sub))
                    if os.path.isdir(sub_full):
                        s="文夹[{}]中有子文件夹，不能导入".format(fullPath)
                        logging.getLogger().warning(s)
                        err_path.append(s)
                        break
                r_path.append(fullPath)

        self.hideInfo()
        if err_file or err_path:
            errstr = '\n'.join(err_file) + '\n' + '\n'.join(err_path)
            self.ui.textBrowser.append(errstr)
            msgBox = QMessageBox(QMessageBox.Critical, u'提示', errstr)
            msgBox.exec_()
            return []
        else:
            return r_path

    @pyqtSlot()
    def on_butPathImport_clicked(self):
        path_lst = self.getAndCheckPaths()
        newPKString = JPDb().LAST_INSERT_ID_SQL()
        self.showInfo(len(path_lst))
        hasError = 0
        SQLS = []
        for i, path in enumerate(path_lst):
            dic = self.getFieldsValues(path)
            fns = ["CONCAT('包含文件：',char(10),REPEAT('-',150))"]
            addFileSQL = []
            subPath = os.listdir(path)
            subPath = ["/".join((path, item)) for item in subPath]
            s = "正在处理{}".format(path)
            logging.getLogger().debug(s)
            self.dispInfo(s, i+1)
            for j, sub in enumerate(subPath):
                fns.append(sqm(os.path.basename(sub)+";"))
                exist, md5FileName, md5BaseName, file_pk = md5Exist(
                    sub, self.con_path)
                if not exist:
                    s = "--->复制【{}】".format(sub)
                    self.dispInfo(s, i+1)
                    logging.getLogger().debug(s)
                    try:
                        toPath = "{}/{}".format(self.con_path, md5FileName)
                        myCopy(sub, toPath)
                        s2 = "insert into t_additionals (original_name,filemd5,"
                        s2 = s2+"file_type) VALUES ('{}',unhex('{}'),'{}');"
                        s2 = [s2.format(os.path.basename(sub),
                                        md5BaseName, getExName(sub)), newPKString]
                        isOK, pk = JPDb().executeTransaction(s2)
                        addFileSQL.append(
                            "select {} into @file_pk{};".format(pk, j))
                    except Exception as e:
                        hasError += 1
                        t = '上传文件过程出现错误，档案未上传，错误信息为：\n{}'
                        logging.getLogger().debug(t)
                        msgBox = QMessageBox(QMessageBox.Critical,
                                             u'提示', t.format(str(e)))
                        msgBox.exec_()
                        print(t)
                else:
                    addFileSQL.append(
                        "SELECT {} INTO @file_pk{};".format(file_pk, j))
                s1 = "insert into t_additionals_archives(archives_pk, file_pk)"
                s1 = s1 + " VALUES(@archive_pk, @file_pk{})"
                addFileSQL.append(s1.format(j))
            dic['archive_describe'] = "CONCAT({})".format(
                (",char(10),").join(fns))
            dic['archive_type'] = sqm(self.archive_type)
            SQLS.append(self.getInsertArchiveSQL('50', dic))
            SQLS.append("{} INTO @archive_pk;".format(newPKString))
            SQLS = SQLS + addFileSQL
            try:
                JPDb().executeTransaction(SQLS)
                SQLS = []
            except Exception as e:
                hasError += 1
                t = '执行增加档案SQL中出现错误,档案并未实际添加，错误信息为：\n{}\n执行SQL为\n{}'
                strSql = '\n'.join(SQLS)
                errStr = t.format(str(e), strSql)
                msgBox = QMessageBox(QMessageBox.Critical,
                                     u'提示', errStr)
                msgBox.exec_()
        QMessageBox.information(self, '提示', "OK")

    @pyqtSlot()
    def on_butFileImport_clicked(self):

        def getInsertAndFileSQL():
            return
        QF = QFileDialog.getOpenFileNames
        fns, filetype = QF(self,
                           "Select a File",
                           JPPub().getOrSetlastOpenDir(),  # 起始路径
                           "Files (*.jpg *.PDF *.doc *.docx *.xls *.xlsx)")
        if not fns:
            return
        JPPub().getOrSetlastOpenDir(fns[0])
        newPKString = JPDb().LAST_INSERT_ID_SQL()
        self.showInfo(len(fns))
        hasError = 0
        for i, original_path in enumerate(fns):
            SQLS = []
            s = "检查是否存在数据库中{}".format(original_path)
            logging.getLogger().debug(s)
            self.dispInfo(s, i+1)
            exist, md5FileName, md5BaseName, file_pk = md5Exist(
                original_path, self.con_path)
            fldValues = self.getFieldsValues(original_path)
            SQLS.append(self.getInsertArchiveSQL(self.archive_type, fldValues))
            SQLS.append("{} INTO @archive_pk;".format(newPKString))
            if exist:
                SQLS.append("select {} into @file_pk;".format(file_pk))
            else:
                s2 = "insert into t_additionals (original_name,filemd5"
                s2 = s2 + ",file_type) VALUES ('{}',unhex('{}'),'{}');"
                SQLS.append(s2.format(os.path.basename(original_path),
                                      md5BaseName, getExName(original_path)))
                SQLS.append("{} INTO @file_pk;".format(newPKString))
            s1 = "insert into t_additionals_archives(archives_pk, file_pk)"
            s1 = s1+" VALUES (@archive_pk,@file_pk);"
            SQLS.append(s1)
            if not exist:
                s = "复制【{}】".format(original_path)
                logging.getLogger().debug(s)
                self.dispInfo(s, i+1)
                try:
                    toPath = "{}/{}".format(self.con_path, md5FileName)
                    myCopy(original_path, toPath)
                except Exception as e:
                    hasError += 1
                    t = '上传文件过程出现错误，档案未上传，错误信息为：\n{}'
                    logging.getLogger().debug(t)
                    msgBox = QMessageBox(QMessageBox.Critical,
                                         u'提示', t.format(str(e)))
                    msgBox.exec_()
            try:
                JPDb().executeTransaction(SQLS)
            except Exception as e:
                hasError += 1
                t = '执行增加档案SQL中出现错误,档案并未实际添加，错误信息为：\n{}\n执行SQL为\n{}'
                strSql = '\n'.join(SQLS)
                errStr = t.format(str(e), strSql)
                logging.getLogger().error("生成的导入文件夹SQL错误："+strSql)
                msgBox = QMessageBox(QMessageBox.Critical,
                                     u'提示', errStr)
                msgBox.exec_()

        # 循环执行完后报告
        else:
            self.hideInfo()
            okStr = "完成但出现{}个错误".format(hasError) if hasError else "完成"
            QMessageBox.information(self, '提示', okStr)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form_Tools()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
