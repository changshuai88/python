# 运行主循环

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyperclip  # 用于复制到剪贴板

def convert_to_chinese(s):
    num_map = {
        '0': '零', '1': '一', '2': '二', '3': '三', 
        '4': '四', '5': '五', '6': '六', '7': '七', 
        '8': '八', '9': '九', '-': '杠'
    }
    return ''.join(num_map.get(char, char) for char in s)

def on_convert():
    input_text = entry.get().strip()
    if not input_text:
        messagebox.showwarning("提示", "请输入要转换的字符串")
        return
    try:
        converted = convert_to_chinese(input_text)
        result_text.delete(1.0, tk.END)  # 清空结果框
        result_text.insert(tk.END, converted)
        # 启用复制按钮
        copy_button.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("错误", f"转换出错: {str(e)}")

def on_copy():
    result = result_text.get(1.0, tk.END).strip()
    if result:
        pyperclip.copy(result)
        # 显示复制成功提示
        status_var.set("已复制到剪贴板!")
        root.after(2000, lambda: status_var.set(""))  # 2秒后清除提示
    else:
        messagebox.showwarning("提示", "没有可复制的内容")

# 创建主窗口
root = tk.Tk()
root.title("数字字符串转中文")
root.geometry("500x300")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# 设置字体
style = ttk.Style()
style.configure("TLabel", font=("SimHei", 10), background="#f0f0f0")
style.configure("TButton", font=("SimHei", 10))
style.configure("TEntry", font=("SimHei", 10))

# 主框架
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 输入部分
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=(0, 15))

input_label = ttk.Label(input_frame, text="输入数字字符串:")
input_label.pack(anchor=tk.W, pady=(0, 5))

entry = ttk.Entry(input_frame, width=40)
entry.pack(anchor=tk.W, fill=tk.X)
entry.focus_set()  # 自动聚焦到输入框

# 按钮部分
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=(0, 15))

convert_button = ttk.Button(button_frame, text="转换", command=on_convert)
convert_button.pack(side=tk.LEFT, padx=(0, 10))

copy_button = ttk.Button(button_frame, text="复制结果", command=on_copy, state=tk.DISABLED)
copy_button.pack(side=tk.LEFT)

# 结果显示部分
result_label = ttk.Label(main_frame, text="转换结果:")
result_label.pack(anchor=tk.W, pady=(0, 5))

result_text = scrolledtext.ScrolledText(main_frame, width=55, height=8, wrap=tk.WORD)
result_text.pack(fill=tk.BOTH, expand=True)
result_text.config(state=tk.NORMAL)  # 可编辑状态，方便选择文本

# 状态栏
status_var = tk.StringVar()
status_label = ttk.Label(main_frame, textvariable=status_var, foreground="green")
status_label.pack(anchor=tk.W, pady=(10, 0))

# 绑定回车键触发转换
root.bind('<Return>', lambda event: on_convert())

# 运行主循环
root.mainloop()