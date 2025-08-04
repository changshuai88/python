
import os
from datetime import datetime
'''
获取name文件夹中的文件名字，并创建关键词，追加到keyword文件中
'''
 
# 获取当前日期
current_date = datetime.now().strftime('%Y-%m-%d')
 
# 打开文件，以追加模式写入
with open('./其他品牌.txt', 'a',encoding='utf-8') as file:
    file.write(current_date + '上传到抖音的照片\n')  # 追加日期，并在末尾添加一个换行符
# 指定文件夹路径
folder_path = './name'
 
# 获取文件夹中的所有文件名
file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
 
#去掉文件后缀 
for i in range(len(file_names)):
    file_names[i]=file_names[i].split('.')[0]    
    with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write(file_names[i]+'\n')
    # print(file_names[i])
#打印结果 列表
# print(file_names)
# key_word = []
for i in range(len(file_names)):
    file_names[i] = "#" + file_names[i]
    #将文件名加#，成为关键字写入到txt文件中
    with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write(file_names[i]+'\n')
#写一条分割线
with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write('-----------------------------------------------------\n')
=======
import os
from datetime import datetime
'''
获取name文件夹中的文件名字，并创建关键词，追加到keyword文件中
'''
 
# 获取当前日期
current_date = datetime.now().strftime('%Y-%m-%d')
 
# 打开文件，以追加模式写入
with open('./其他品牌.txt', 'a',encoding='utf-8') as file:
    file.write(current_date + '上传到抖音的照片\n')  # 追加日期，并在末尾添加一个换行符
# 指定文件夹路径
folder_path = './name'
 
# 获取文件夹中的所有文件名
file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
 
#去掉文件后缀 
for i in range(len(file_names)):
    file_names[i]=file_names[i].split('.')[0]    
    with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write(file_names[i]+'\n')
    # print(file_names[i])
#打印结果 列表
# print(file_names)
# key_word = []
for i in range(len(file_names)):
    file_names[i] = "#" + file_names[i]
    #将文件名加#，成为关键字写入到txt文件中
    with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write(file_names[i]+'\n')
#写一条分割线
with open('./其他品牌.txt', 'a', encoding='utf-8') as file:
        file.write('-----------------------------------------------------\n')
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
print("读取写入完毕")