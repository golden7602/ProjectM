from PIL import Image
import os


img = Image.open('E:\\ProjectM\\temp\\20_20200612134400\\1.jpg')  # 读取系统的内照片
img = img.convert("RGBA")  # 转换获取信息
pixdata = img.load()

for y in range(img.size[1]):
    for x in range(img.size[0]):
        if pixdata[x, y][0] > 220 and pixdata[x, y][1] > 220 and pixdata[x, y][2] > 220 and pixdata[x, y][3] > 220:
            pixdata[x, y] = (255, 255, 255, 0)
img.save(r'E:\\ProjectM\\temp\\20_20200612134400\\2.png')  # 保存修改像素点后的图片
