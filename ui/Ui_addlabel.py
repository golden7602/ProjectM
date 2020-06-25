#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import reportlab
helpDoc = '''
Add Page Number to PDF file with Python
Python 给 PDF 添加 页码
usage:
    python addPageNumberToPDF.py [PDF path]
require:
    pip install reportlab pypdf2
    Support both Python2/3, But more recommend Python3

tips:
    * output file will save at pdfWithNumbers/[PDF path]_page.pdf
    * only support A4 size PDF
    * tested on Python2/Python3@ubuntu
    * more large size of PDF require more RAM
    * if segmentation fault, plaese try use Python 3
    * if generate PDF document is damaged, plaese try use Python 3

Author:
    Lei Yang (ylxx@live.com)

GitHub:
    https://gist.github.com/DIYer22/b9ede6b5b96109788a47973649645c1f
'''
print(helpDoc)








if __name__ == "__main__":

    # 需要标页码的pdf文件
    writePageNumToPdf('Z:\\01.pdf')
