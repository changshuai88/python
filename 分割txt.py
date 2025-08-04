<<<<<<< HEAD
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pathlib import Path

class TextSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本文件分割工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TProgressbar", thickness=20)
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 设置部分
        settings_frame = ttk.LabelFrame(main_frame, text="分割设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="分割数量:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.num_parts_var = tk.IntVar(value=5)
        num_parts_spinbox = ttk.Spinbox(settings_frame, from_=2, to=10, textvariable=self.num_parts_var, width=5)
        num_parts_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=100, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        split_btn = ttk.Button(btn_frame, text="开始分割", command=self.split_file)
        split_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = ttk.Button(btn_frame, text="退出", command=self.root.destroy)
        exit_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.CENTER)
        status_label.pack(fill=tk.X, pady=10)
        
        # 设置列权重，使界面可伸缩
        file_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def browse_file(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")
    
    def split_file(self):
        """执行文件分割操作"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请选择一个文本文件")
            return
        
        if not os.path.isfile(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        if not file_path.lower().endswith('.txt'):
            messagebox.showerror("错误", "请选择txt格式的文件")
            return
        
        try:
            num_parts = self.num_parts_var.get()
            self.status_var.set("正在分割文件...")
            self.root.update()  # 更新UI
            
            # 读取文件并按段落分割
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按空行分割成段落
            paragraphs = content.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            if not paragraphs:
                messagebox.showwarning("警告", "文件中未找到有效段落！")
                self.status_var.set("就绪")
                return
            
            # 计算每个部分应包含的段落数
            parts = []
            base_size, remainder = divmod(len(paragraphs), num_parts)
            
            start_idx = 0
            for i in range(num_parts):
                part_size = base_size + (1 if i < remainder else 0)
                end_idx = start_idx + part_size
                parts.append(paragraphs[start_idx:end_idx])
                start_idx = end_idx
            
            # 创建输出目录
            input_path = Path(file_path)
            output_dir = input_path.parent / f"{input_path.stem}_split"
            os.makedirs(output_dir, exist_ok=True)
            
            # 中文数字映射
            chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
            
            # 写入各个部分
            for i, part in enumerate(parts):
                # 更新进度条
                progress = (i + 1) / num_parts * 100
                self.progress_var.set(progress)
                self.status_var.set(f"正在写入文件 {i+1}/{num_parts}...")
                self.root.update()
                
                # 构建输出文件名（原文件名+中文数字）
                output_file = output_dir / f"{input_path.stem}_{chinese_nums[i]}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(part))
            
            self.progress_var.set(100)
            self.status_var.set(f"文件已成功切分为{num_parts}个部分")
            messagebox.showinfo("成功", f"文件已成功切分为{num_parts}个部分\n保存在: {output_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"分割文件时出错: {str(e)}")
            self.status_var.set("就绪")
        finally:
            self.progress_var.set(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextSplitterApp(root)
=======
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from pathlib import Path

class TextSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本文件分割工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TProgressbar", thickness=20)
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 设置部分
        settings_frame = ttk.LabelFrame(main_frame, text="分割设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="分割数量:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.num_parts_var = tk.IntVar(value=5)
        num_parts_spinbox = ttk.Spinbox(settings_frame, from_=2, to=10, textvariable=self.num_parts_var, width=5)
        num_parts_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, length=100, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        split_btn = ttk.Button(btn_frame, text="开始分割", command=self.split_file)
        split_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = ttk.Button(btn_frame, text="退出", command=self.root.destroy)
        exit_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.CENTER)
        status_label.pack(fill=tk.X, pady=10)
        
        # 设置列权重，使界面可伸缩
        file_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def browse_file(self):
        """打开文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")
    
    def split_file(self):
        """执行文件分割操作"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请选择一个文本文件")
            return
        
        if not os.path.isfile(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
        
        if not file_path.lower().endswith('.txt'):
            messagebox.showerror("错误", "请选择txt格式的文件")
            return
        
        try:
            num_parts = self.num_parts_var.get()
            self.status_var.set("正在分割文件...")
            self.root.update()  # 更新UI
            
            # 读取文件并按段落分割
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按空行分割成段落
            paragraphs = content.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            if not paragraphs:
                messagebox.showwarning("警告", "文件中未找到有效段落！")
                self.status_var.set("就绪")
                return
            
            # 计算每个部分应包含的段落数
            parts = []
            base_size, remainder = divmod(len(paragraphs), num_parts)
            
            start_idx = 0
            for i in range(num_parts):
                part_size = base_size + (1 if i < remainder else 0)
                end_idx = start_idx + part_size
                parts.append(paragraphs[start_idx:end_idx])
                start_idx = end_idx
            
            # 创建输出目录
            input_path = Path(file_path)
            output_dir = input_path.parent / f"{input_path.stem}_split"
            os.makedirs(output_dir, exist_ok=True)
            
            # 中文数字映射
            chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
            
            # 写入各个部分
            for i, part in enumerate(parts):
                # 更新进度条
                progress = (i + 1) / num_parts * 100
                self.progress_var.set(progress)
                self.status_var.set(f"正在写入文件 {i+1}/{num_parts}...")
                self.root.update()
                
                # 构建输出文件名（原文件名+中文数字）
                output_file = output_dir / f"{input_path.stem}_{chinese_nums[i]}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(part))
            
            self.progress_var.set(100)
            self.status_var.set(f"文件已成功切分为{num_parts}个部分")
            messagebox.showinfo("成功", f"文件已成功切分为{num_parts}个部分\n保存在: {output_dir}")
            
        except Exception as e:
            messagebox.showerror("错误", f"分割文件时出错: {str(e)}")
            self.status_var.set("就绪")
        finally:
            self.progress_var.set(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextSplitterApp(root)
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
    root.mainloop()