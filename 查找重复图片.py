import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import defaultdict
import threading

class DuplicateFileFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("重复文件查找工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("SimHei", 10, "bold"))
        self.style.configure("Treeview", font=("SimHei", 10))
        
        self.selected_dir = tk.StringVar()
        
        # 创建界面组件
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部框架：文件夹选择
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="选择文件夹:", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)
        
        ttk.Entry(top_frame, textvariable=self.selected_dir, width=50, font=("SimHei", 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(top_frame, text="浏览...", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="开始查找", command=self.start_search).pack(side=tk.LEFT, padx=5)
        
        # 中间框架：结果显示
        mid_frame = ttk.Frame(self.root, padding="10")
        mid_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树状视图显示结果
        columns = ("文件名", "出现次数", "路径")
        self.result_tree = ttk.Treeview(mid_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col)
            if col == "路径":
                self.result_tree.column(col, width=400, anchor=tk.W)
            else:
                self.result_tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        scrollbar_x = ttk.Scrollbar(mid_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 底部框架：状态信息
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="就绪，请选择文件夹并点击开始查找")
        ttk.Label(bottom_frame, textvariable=self.status_var, font=("SimHei", 9)).pack(anchor=tk.W)
        
    def browse_directory(self):
        """打开文件对话框选择文件夹"""
        directory = filedialog.askdirectory(title="选择要扫描的文件夹")
        if directory:
            self.selected_dir.set(directory)
    
    def start_search(self):
        """开始查找重复文件（在新线程中执行以避免界面冻结）"""
        directory = self.selected_dir.get()
        
        if not directory:
            messagebox.showwarning("警告", "请先选择一个文件夹")
            return
            
        if not os.path.exists(directory):
            messagebox.showerror("错误", f"文件夹不存在: {directory}")
            return
            
        if not os.path.isdir(directory):
            messagebox.showerror("错误", f"这不是一个文件夹: {directory}")
            return
        
        # 清空之前的结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 更新状态并禁用按钮
        self.status_var.set(f"正在扫描 {directory} 及其子文件夹...")
        self.root.update()
        
        # 在新线程中执行扫描，避免界面冻结
        threading.Thread(target=self.find_duplicates, args=(directory,), daemon=True).start()
    
    def find_duplicates(self, root_dir):
        """查找重复文件并更新界面"""
        # 存储文件名和对应的路径列表
        file_names = defaultdict(list)
        
        # 遍历目录及其子目录
        total_files = 0
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                total_files += 1
                # 每处理100个文件更新一次状态
                if total_files % 100 == 0:
                    self.status_var.set(f"已扫描 {total_files} 个文件...")
                    self.root.update_idletasks()
                
                full_path = os.path.join(dirpath, filename)
                file_names[filename].append(full_path)
        
        # 筛选出有多个路径的文件名（即重名文件）
        duplicates = {name: paths for name, paths in file_names.items() if len(paths) > 1}
        
        # 更新结果到界面
        self.root.after(0, self.update_results, duplicates, total_files)
    
    def update_results(self, duplicates, total_files):
        """更新界面显示结果"""
        if not duplicates:
            self.status_var.set(f"扫描完成，共检查 {total_files} 个文件，未发现重复文件")
            messagebox.showinfo("结果", "未发现重复文件")
            return
        
        # 显示重复文件
        for name, paths in duplicates.items():
            # 插入文件名和出现次数
            self.result_tree.insert("", tk.END, values=(name, len(paths), paths[0]))
            # 插入其余路径，文件名和出现次数留空
            for path in paths[1:]:
                self.result_tree.insert("", tk.END, values=("", "", path))
        
        self.status_var.set(f"扫描完成，共检查 {total_files} 个文件，发现 {len(duplicates)} 组重复文件")
        messagebox.showinfo("结果", f"发现 {len(duplicates)} 组重复文件")

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFileFinder(root)
    root.mainloop()
    