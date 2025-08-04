import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
from typing import List, Set

def get_file_names(directory: str) -> Set[str]:
    """获取目录及其子目录中所有文件的名称（不包含路径）"""
    file_names = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_names.add(file)
    return file_names

def find_matching_files(source_dir: str, target_dir: str) -> List[str]:
    """在目标目录中查找与源目录中文件名相同的所有文件"""
    source_files = get_file_names(source_dir)
    matching_files = []
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file in source_files:
                matching_files.append(os.path.join(root, file))
    
    return matching_files

def delete_files(file_paths: List[str], progress_callback=None) -> None:
    """删除文件列表中的所有文件，并通过回调函数报告进度"""
    total_files = len(file_paths)
    
    if total_files == 0:
        if progress_callback:
            progress_callback(0, "没有找到需要删除的文件。")
        return
    
    for i, file_path in enumerate(file_paths, 1):
        try:
            os.remove(file_path)
            status = f"已成功删除：{file_path}"
        except Exception as e:
            status = f"删除失败：{file_path}，错误：{e}"
        
        if progress_callback:
            progress_callback(i / total_files, status)

class FileDeletionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件匹配删除工具")
        self.root.geometry("700x500")
        
        # 设置中文字体支持
        self.root.option_add("*Font", "SimHei 10")
        
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.status_text = tk.StringVar(value="请选择源文件夹和目标文件夹")
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建选择文件夹的框架
        folder_frame = ttk.LabelFrame(self.root, text="文件夹选择")
        folder_frame.pack(fill="x", padx=10, pady=5)
        
        # 源文件夹选择
        ttk.Label(folder_frame, text="源文件夹 (提供文件名):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.source_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(folder_frame, text="浏览...", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)
        
        # 目标文件夹选择
        ttk.Label(folder_frame, text="目标文件夹 (查找并删除):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.target_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(folder_frame, text="浏览...", command=self.browse_target).grid(row=1, column=2, padx=5, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="查找匹配文件", command=self.find_files).pack(side="left", padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side="right", padx=5)
        
        # 状态框架
        status_frame = ttk.LabelFrame(self.root, text="状态")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(status_frame, variable=self.progress_var, length=100).pack(fill="x", padx=5, pady=5)
        
        # 状态文本
        ttk.Label(status_frame, textvariable=self.status_text, wraplength=680).pack(anchor="w", padx=5, pady=5)
        
        # 匹配文件列表
        ttk.Label(status_frame, text="匹配的文件:").pack(anchor="w", padx=5, pady=5)
        
        self.file_listbox = tk.Listbox(status_frame, height=10, width=80)
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.file_listbox, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # 删除按钮
        self.delete_button = ttk.Button(status_frame, text="确认删除选中文件", command=self.confirm_deletion, state="disabled")
        self.delete_button.pack(pady=5)
    
    def browse_source(self):
        directory = filedialog.askdirectory(title="选择源文件夹")
        if directory:
            self.source_dir.set(directory)
    
    def browse_target(self):
        directory = filedialog.askdirectory(title="选择目标文件夹")
        if directory:
            self.target_dir.set(directory)
    
    def find_files(self):
        source_dir = self.source_dir.get()
        target_dir = self.target_dir.get()
        
        if not source_dir or not target_dir:
            messagebox.showerror("错误", "请选择源文件夹和目标文件夹")
            return
        
        if not os.path.isdir(source_dir) or not os.path.isdir(target_dir):
            messagebox.showerror("错误", "选择的路径不是有效的文件夹")
            return
        
        self.status_text.set("正在查找匹配的文件...")
        self.progress_var.set(0)
        self.file_listbox.delete(0, tk.END)
        
        # 在单独的线程中执行查找操作，避免界面卡顿
        threading.Thread(target=self._find_files_thread, daemon=True).start()
    
    def _find_files_thread(self):
        try:
            source_dir = self.source_dir.get()
            target_dir = self.target_dir.get()
            
            self.matching_files = find_matching_files(source_dir, target_dir)
            
            self.root.after(0, self._update_ui_after_find)
        except Exception as e:
            self.root.after(0, lambda: self.status_text.set(f"查找过程中出错: {str(e)}"))
    
    def _update_ui_after_find(self):
        if not self.matching_files:
            self.status_text.set("没有找到匹配的文件")
            self.delete_button.config(state="disabled")
            return
        
        self.status_text.set(f"找到 {len(self.matching_files)} 个匹配的文件")
        self.delete_button.config(state="normal")
        
        for file_path in self.matching_files:
            self.file_listbox.insert(tk.END, file_path)
    
    def confirm_deletion(self):
        selected_indices = self.file_listbox.curselection()
        
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要删除的文件")
            return
        
        selected_files = [self.matching_files[i] for i in selected_indices]
        file_count = len(selected_files)
        
        if file_count == 0:
            messagebox.showinfo("提示", "请选择要删除的文件")
            return
        
        # 确认对话框
        answer = messagebox.askyesno(
            "确认删除", 
            f"确定要删除选中的 {file_count} 个文件吗？\n此操作不可撤销！"
        )
        
        if not answer:
            return
        
        self.status_text.set("正在删除文件...")
        self.progress_var.set(0)
        self.delete_button.config(state="disabled")
        
        # 在单独的线程中执行删除操作
        threading.Thread(target=delete_files, args=(selected_files, self.update_progress), daemon=True).start()
    
    def update_progress(self, progress, status):
        self.root.after(0, lambda: self.progress_var.set(progress * 100))
        self.root.after(0, lambda: self.status_text.set(status))
        
        if progress == 1:
            self.root.after(0, lambda: self.delete_button.config(state="normal"))

def main():
    root = tk.Tk()
    app = FileDeletionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()    