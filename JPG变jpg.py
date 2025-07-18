# import os

# def rename_jpg_files(directory):
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.upper().endswith('.JPG'):
#                 old_file_path = os.path.join(root, file)
#                 new_file_name = file[:-3] + 'jpg'
#                 new_file_path = os.path.join(root, new_file_name)
#                 try:
#                     os.rename(old_file_path, new_file_path)
#                     print(f"已将 {old_file_path} 重命名为 {new_file_path}")
#                 except Exception as e:
#                     print(f"重命名 {old_file_path} 时出错: {e}")

# if __name__ == "__main__":
#     # 请替换为你要处理的文件夹路径
#     target_directory = 'E:\work\卡特\卡特照片\卡特照片2025'
#     rename_jpg_files(target_directory)
    
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def rename_jpg_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.upper().endswith('.JPG'):
                old_file_path = os.path.join(root, file)
                new_file_name = file[:-3] + 'jpg'
                new_file_path = os.path.join(root, new_file_name)
                try:
                    os.rename(old_file_path, new_file_path)
                    print(f"已将 {old_file_path} 重命名为 {new_file_path}")
                except Exception as e:
                    print(f"重命名 {old_file_path} 时出错: {e}")


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)


def start_processing():
    directory = entry_directory.get()
    if directory:
        rename_jpg_files(directory)
        messagebox.showinfo("完成", "处理完毕！")


# 创建主窗口
root = tk.Tk()
root.title("JPG 文件重命名工具")

# 创建并布局组件
label_directory = tk.Label(root, text="选择文件夹:")
label_directory.pack(pady=10)

entry_directory = tk.Entry(root, width=50)
entry_directory.pack(pady=5)

button_select = tk.Button(root, text="选择文件夹", command=select_directory)
button_select.pack(pady=10)

button_start = tk.Button(root, text="开始处理", command=start_processing)
button_start.pack(pady=20)

# 运行主循环
root.mainloop()
    