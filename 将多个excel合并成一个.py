import os
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def merge_excel_files(input_dir, output_file, progress_callback=None):
    """
    将指定目录下的所有 Excel 文件合并到一个新的 Excel 文件中
    
    参数:
    input_dir (str): 包含 Excel 文件的目录路径
    output_file (str): 输出文件的路径
    progress_callback (function, optional): 进度回调函数
    
    返回:
    str: 合并后的文件路径或错误信息
    """
    # 获取目录中所有 Excel 文件
    excel_files = [f for f in os.listdir(input_dir) 
                  if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
    
    if not excel_files:
        return "在指定目录中未找到 Excel 文件"
    
    total_files = len(excel_files)
    
    try:
        # 创建一个 ExcelWriter 对象
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 处理每个 Excel 文件
            for i, file in enumerate(excel_files):
                file_path = os.path.join(input_dir, file)
                try:
                    # 读取 Excel 文件的所有表页
                    xls = pd.ExcelFile(file_path)
                    sheet_names = xls.sheet_names
                    
                    # 处理每个表页
                    for sheet_name in sheet_names:
                        df = xls.parse(sheet_name)
                        
                        # 创建表页名称，格式为 "文件名_表页名"
                        # 限制表页名长度不超过 31 个字符（Excel 限制）
                        sheet_title = f"{os.path.splitext(file)[0]}_{sheet_name}"
                        sheet_title = sheet_title[:31] if len(sheet_title) > 31 else sheet_title
                        
                        # 将数据写入新 Excel 文件
                        df.to_excel(writer, sheet_name=sheet_title, index=False)
                    
                    # 更新进度
                    if progress_callback:
                        progress = (i + 1) / total_files * 100
                        progress_callback(f"已处理: {file}", progress)
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"处理文件 {file} 时出错: {str(e)}", 
                                         (i + 1) / total_files * 100)
    except Exception as e:
        return f"合并过程中出错: {str(e)}"
    
    return output_file

class ExcelMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 文件合并工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        ttk.Label(main_frame, text="源文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.source_dir_var = tk.StringVar()
        source_entry = ttk.Entry(main_frame, textvariable=self.source_dir_var, width=50)
        source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        browse_btn = ttk.Button(main_frame, text="浏览...", command=self.browse_source_dir)
        browse_btn.grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        
        # 输出文件选择
        ttk.Label(main_frame, text="输出文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.output_file_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        save_btn = ttk.Button(main_frame, text="保存为...", command=self.select_output_file)
        save_btn.grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        
        # 状态显示
        ttk.Label(main_frame, text="状态:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                anchor=tk.W, justify=tk.LEFT)
        status_label.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=100)
        progress_bar.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 日志显示
        ttk.Label(main_frame, text="处理日志:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        
        self.log_text = tk.Text(main_frame, height=10, width=50, wrap=tk.WORD)
        self.log_text.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        scrollbar = ttk.Scrollbar(main_frame, command=self.log_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S), pady=5)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=10)
        
        self.merge_btn = ttk.Button(btn_frame, text="开始合并", command=self.start_merge)
        self.merge_btn.pack(side=tk.RIGHT, padx=5)
        
        # 设置网格权重，使界面可缩放
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 默认值
        default_output = os.path.join(os.getcwd(), 
                                     f"合并文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        self.output_file_var.set(default_output)
        
    def browse_source_dir(self):
        directory = filedialog.askdirectory(title="选择源文件夹")
        if directory:
            self.source_dir_var.set(directory)
            
            # 自动生成输出文件名
            default_output = os.path.join(directory, 
                                         f"合并文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            self.output_file_var.set(default_output)
    
    def select_output_file(self):
        initial_dir = self.source_dir_var.get() or os.getcwd()
        filename = filedialog.asksaveasfilename(
            title="保存输出文件",
            initialdir=initial_dir,
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def update_status(self, message, progress):
        self.status_var.set(message)
        self.progress_var.set(progress)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def merge_complete(self, result):
        self.merge_btn.config(state=tk.NORMAL)
        if isinstance(result, str) and result.startswith("在指定目录中未找到"):
            messagebox.showwarning("警告", result)
        elif isinstance(result, str) and result.startswith("合并过程中出错"):
            messagebox.showerror("错误", result)
        else:
            messagebox.showinfo("成功", f"合并完成！文件已保存至:\n{result}")
    
    def start_merge(self):
        source_dir = self.source_dir_var.get()
        output_file = self.output_file_var.get()
        
        if not source_dir:
            messagebox.showerror("错误", "请选择源文件夹")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 禁用按钮防止重复点击
        self.merge_btn.config(state=tk.DISABLED)
        
        # 在新线程中执行合并操作
        threading.Thread(
            target=lambda: self.merge_complete(
                merge_excel_files(source_dir, output_file, self.update_status)
            ),
            daemon=True
        ).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelMergerApp(root)
    root.mainloop()    