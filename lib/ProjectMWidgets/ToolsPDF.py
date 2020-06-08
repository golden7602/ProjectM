

from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image as PLIImage
from Ui.Ui_FormToolsPDF import Ui_Form as Ui_Form_Tools
from lib.JPPublc import JPPub
from PyQt5.QtWidgets import (QMessageBox, QFileDialog, QDialog)
from PyQt5.QtCore import (QDate, QMetaObject, pyqtSlot, Qt, QModelIndex)
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QGuiApplication, QCursor)
import os


class FileToolsPDF(QDialog):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        pub = JPPub()
        super().__init__(parent=pub.MainForm, flags=flags)
        self.setWindowTitle("工具集")
        self.ui = Ui_Form_Tools()
        self.ui.setupUi(self)
        self.addtionalInfo = []
        self.MainForm = pub.MainForm
        self.ui.label_pdf.setPixmap(self.MainForm.getPixmap('file_pdf.png'))
        self.con_path = JPPub().getConfigData()["archives_path"]
        self.ui.pb.setRange(0, 0)
        self.ui.pb.hide()
        self.ui.label_info.hide()
        self.exec_()

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

    @pyqtSlot()
    def on_butPic2PDF_clicked(self):

        QF = QFileDialog.getOpenFileNames
        fns, filetype = QF(self,
                           "Select a File",
                           JPPub().getOrSetlastOpenDir(),  # 起始路径
                           "Files (*.jpg *.PNG)")
        if not fns:
            return
        JPPub().getOrSetlastOpenDir(fns[0])
        initName = ''.join([os.path.splitext(fns[0])[0], ".PDF"])
        pdf_name, filetype = QFileDialog.getSaveFileName(
            self, "输入保存文件名", initName, 'Files (*.PDF)')
        if not pdf_name:
            return
        im_list = []
        if fns:
            im1 = PLIImage.open(fns[0])
            for i in range(1, len(fns)):
                img = PLIImage.open(fns[i])
                if img.mode == "RGBA":
                    img = img.convert('RGB')
                    im_list.append(img)
                else:
                    im_list.append(img)
        if pdf_name:
            im1.save(pdf_name, resolution=100.0,
                     save_all=True, append_images=im_list)
            QMessageBox.information(self, '提示', 'OK')

    @pyqtSlot()
    def on_butSplitPDF_clicked(self):

        QF = QFileDialog.getOpenFileName
        fns, filetype = QF(self,
                           "Select a File",
                           JPPub().getOrSetlastOpenDir(),  # 起始路径
                           "Files (*.PDF)")
        if not fns:
            return
        JPPub().getOrSetlastOpenDir(fns)
        fInput = open(fns, 'rb')
        pdf_input = PdfFileReader(fInput)
        page_count = pdf_input.getNumPages()

        # 进行切分
        self.showInfo(page_count)
        for num in range(0, page_count):
            txt = "共{}页，正在拆分第{}页...".format(page_count, num)
            self.dispInfo(txt, num+1)
            pdf_output = PdfFileWriter()
            name_ex = "_" + str(num+1).zfill(4) + ".pdf"
            outfn_name = os.path.splitext(fns)[0] + name_ex
            pdf_output.addPage(pdf_input.getPage(num))
            with open(outfn_name, 'wb') as tofile:
                pdf_output.write(tofile)
        fInput.close()
        self.dispInfo('拆分完成！', page_count)

    @pyqtSlot()
    def on_butMergePDF_clicked(self):
        output = PdfFileWriter()
        outputPages = 0
        QF = QFileDialog.getOpenFileNames
        pdf_fileName, filetype = QF(self,
                                    "Select a File",
                                    JPPub().getOrSetlastOpenDir(),  # 起始路径
                                    "Files (*.PDF)")
        if not pdf_fileName:
            return
        JPPub().getOrSetlastOpenDir(pdf_fileName[0])
        i = 0
        pdf_fileName.sort()
        fopen = []
        self.showInfo(len(pdf_fileName))
        for i, fn in enumerate(pdf_fileName):
            # 读取源pdf文件
            temp = open(fn, "rb")
            fopen.append(temp)
            inputF = PdfFileReader(temp)
            # 如果pdf文件已经加密，必须首先解密才能使用pyPdf
            if inputF.isEncrypted == True:
                inputF.decrypt("map")

            # 获得源pdf文件中页面总数
            pageCount = inputF.getNumPages()
            outputPages += pageCount

            # 分别将page添加到输出output中
            self.dispInfo("正在合并【{}】".format(pdf_fileName[i]), i)
            for iPage in range(0, pageCount):
                output.addPage(inputF.getPage(iPage))

        # 最后写pdf文件
        out_file_path = ''.join([os.path.splitext(pdf_fileName[0])[0],
                                 "_至_",
                                 os.path.basename(
                                     pdf_fileName[len(pdf_fileName)-1]),
                                 r'合并后.PDF'])
        self.dispInfo("正在写入【{}】...".format(out_file_path), i)
        outputStream = open(out_file_path, "wb")
        output.write(outputStream)
        outputStream.close()
        for i in fopen:
            i.close()
        self.dispInfo("写入完成！", len(pdf_fileName))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form_Tools()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
