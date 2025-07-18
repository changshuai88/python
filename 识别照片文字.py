import pytesseract
from PIL import Image
 
# 指定tesseract的安装路径（如果需要）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
 
# 打开图片
# image = Image.open('./img/IMG_5923.jpg')
 
# # 使用pytesseract识别图片中的文字
# text = pytesseract.image_to_string(image, lang='eng')  # 'eng'表示使用英语模型，也可以改为其他语言代码，如'chi_sim'表示简体中文
 
# # 打印识别的文字
# print(text)
# # 识别中文
# text_chinese = pytesseract.image_to_string(image, lang='chi_sim')  # 简体中文
# print('识别出的中文文本：', text_chinese)

import cv2
import numpy as np
# 指定tesseract的安装路径（如果需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 使用 OpenCV 读取图像
image_cv = cv2.imread('./img/222.jpg')

# 转为灰度图
gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

# 应用二值化处理
_, binary_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)

# 使用 pytesseract 识别处理后的图像
# text_processed = pytesseract.image_to_string(binary_image, lang='eng')
text_processed = pytesseract.image_to_string(binary_image, lang='chi_sim')

print('处理后的识别文本：', text_processed)














# import os

#!/usr/bin/python3

# import os, sys

# # 打开文件
# path = "E:\work\卡特\卡特照片"
# dirs = os.listdir( path )

# # 输出所有文件和文件夹
# for file in dirs:
#     print (file) 




# def get_filenames_in_folder(folder_path):
#     filenames = []
#     for filename in os.listdir(folder_path):
#         if os.path.isfile(os.path.join(folder_path, filename)):
#             filenames.append(filename)
#     return filenames