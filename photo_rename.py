import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os



def select_photo():
    file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.png;*.jpeg")])
    if file_path:
        photo_entry.delete(0, tk.END)
        photo_entry.insert(0, file_path)


def select_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx;*.xls")])
    if file_path:
        excel_entry.delete(0, tk.END)
        excel_entry.insert(0, file_path)


def rename_photo():
    photo_path = photo_entry.get()
    excel_path = excel_entry.get()

    if not photo_path or not excel_path:
        result_label.config(text="请选择照片和 Excel 文件！")
        return

    try:
        df = pd.read_excel(excel_path)
        photo_filename = os.path.basename(photo_path)
        name_without_ext = os.path.splitext(photo_filename)[0]
        # print(name_without_ext)
        # df.iloc[:, 2] 这里的2为第三列为件号就是原来照片文件名。
        match_row = df[df.iloc[:, 2] == name_without_ext]
        # print(match_row)
        if not match_row.empty:
            # 这里的match_row.iloc[0, 1]中的1是指第二列为品名
            product_name = match_row.iloc[0, 1]
            new_filename = f"{name_without_ext}_{product_name}{os.path.splitext(photo_filename)[1]}"
            new_path = os.path.join(os.path.dirname(photo_path), new_filename)
            os.rename(photo_path, new_path)
            result_label.config(text=f"照片已重命名为: {new_filename}")
        else:
            result_label.config(text="未在 Excel 中找到对应的品名！")

    except Exception as e:
        result_label.config(text=f"发生错误: {e}")


# 创建主窗口
root = tk.Tk()
root.title("照片重命名工具")

# 创建选择照片的按钮和输入框
photo_label = tk.Label(root, text="选择照片:")
photo_label.pack()
photo_entry = tk.Entry(root, width=50)
photo_entry.pack()
photo_button = tk.Button(root, text="选择照片", command=select_photo)
photo_button.pack()

# 创建选择 Excel 文件的按钮和输入框
excel_label = tk.Label(root, text="选择 Excel 文件:")
excel_label.pack()
excel_entry = tk.Entry(root, width=50)
excel_entry.pack()
excel_button = tk.Button(root, text="选择 Excel 文件", command=select_excel)
excel_button.pack()

# 创建重命名按钮
rename_button = tk.Button(root, text="重命名照片", command=rename_photo)
rename_button.pack()

# 创建结果显示标签
result_label = tk.Label(root, text="")
result_label.pack()

# 运行主循环
root.mainloop()
    