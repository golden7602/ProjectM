from PIL import Image
import os
from PyQt5.QtWidgets import (QFileDialog)


def rea(path, pdf_name):
    file_list = os.listdir(path)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(x)

    pic_name.sort()
    new_pic = []

    for x in pic_name:
        if "jpg" in x:
            new_pic.append(x)

    for x in pic_name:
        if "png" in x:
            new_pic.append(x)

    print("hec", new_pic)

    im1 = Image.open(os.path.join(path, new_pic[0]))
    new_pic.pop(0)
    for i in new_pic:
        img = Image.open(os.path.join(path, i))
        # im_list.append(Image.open(i))
        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    im1.save(pdf_name, "PDF", resolution=100.0,
             save_all=True, append_images=im_list)
    print("输出文件名称：", pdf_name)


if __name__ == '__main__':
    QF = QFileDialog.getOpenFileNames
    fns, filetype = QF(None,
                       "Select a File",
                       '//192.168.1.20/jhglb/JHGLB_PUBLIC',  # 起始路径
                       "Files (*.jpg *.PNG)")
    im_list = []
    if fns:
        im1 = Image.open(fns[0])
        for i in range(1, len(fns)):
            img = Image.open(i)
            if img.mode == "RGBA":
                img = img.convert('RGB')
                im_list.append(img)
            else:
                im_list.append(img)
    pdf_name = QFileDialog.getSaveFileName(None)
    im1.save(pdf_name, "PDF", resolution=100.0,
             save_all=True, append_images=im_list)


    pdf_name = '3D2.pdf'
    if ".pdf" in pdf_name:
        rea(path='', pdf_name=pdf_name)
    else:
        rea(path='', pdf_name="{}.pdf".format(pdf_name))
