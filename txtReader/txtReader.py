import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import json
from datetime import datetime


class TxtReader:
    def __init__(self, root):
        # 初始化主窗口
        self.root = root
        self.root.title("TXT阅读器")
        self.root.geometry("850x650")
        
        # 核心配置与状态变量
        self.current_file = None  # 当前打开的文件路径
        self.current_page = 0
        self.total_pages = 0
        self.pages = []
        self.lines_per_page = 28
        self.font_size = 12
        self.bg_colors = {
            "默认白": "#FFFFFF",
            "护眼米黄": "#F5F2E9",
            "浅灰": "#F0F0F0",
            "浅绿": "#E8F5E9"
        }
        self.current_bg_name = "默认白"  # 记录背景名称（用于保存）
        self.current_bg = self.bg_colors[self.current_bg_name]
        self.text_color = "#333333"
        
        # 历史记录配置
        self.history_file = "reading_history.json"  # 历史记录保存文件
        self.max_history = 10  # 最多保存10条记录
        self.history = self.load_history()  # 加载历史记录
        
        # 创建菜单栏
        self.menu_bar = tk.Menu(root)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="打开文件", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        
        # 历史记录子菜单（动态生成）
        self.history_submenu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="历史记录", menu=self.history_submenu)
        self.update_history_menu()  # 初始化历史记录菜单
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=root.quit, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        
        # 视图菜单
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # 字体子菜单
        self.font_submenu = tk.Menu(self.view_menu, tearoff=0)
        self.font_submenu.add_command(label="放大字体", command=self.increase_font, accelerator="Ctrl++")
        self.font_submenu.add_command(label="缩小字体", command=self.decrease_font, accelerator="Ctrl+-")
        self.view_menu.add_cascade(label="字体大小", menu=self.font_submenu)
        
        # 背景子菜单
        self.bg_submenu = tk.Menu(self.view_menu, tearoff=0)
        for name in self.bg_colors:
            self.bg_submenu.add_command(
                label=name, 
                command=lambda n=name: self.set_background(n)
            )
        self.view_menu.add_cascade(label="阅读背景", menu=self.bg_submenu)
        
        self.menu_bar.add_cascade(label="视图", menu=self.view_menu)
        
        root.config(menu=self.menu_bar)
        
        # 绑定快捷键
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-q>", lambda e: root.quit())
        self.root.bind("<Control-+>", lambda e: self.increase_font())
        self.root.bind("<Control-minus>", lambda e: self.decrease_font())
        self.root.bind("<Prior>", lambda e: self.prev_page())  # PageUp
        self.root.bind("<Next>", lambda e: self.next_page())   # PageDown
        
        # 文本显示区域
        self.text_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.text_widget = tk.Text(
            self.text_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=("SimHei", self.font_size),
            bg=self.current_bg,
            fg=self.text_color,
            bd=0,
            padx=20,
            pady=15
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        self.scrollbar = tk.Scrollbar(
            self.text_frame, 
            command=self.text_widget.yview,
            troughcolor="#EEEEEE",
            width=10
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        
        # 翻页控制区
        self.control_frame = tk.Frame(root, height=40)
        self.control_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.prev_btn = tk.Button(
            self.control_frame, 
            text="上一页 (PageUp)", 
            command=self.prev_page, 
            state=tk.DISABLED,
            padx=10,
            relief=tk.RAISED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=20)
        
        self.page_label = tk.Label(
            self.control_frame, 
            text="第 0 页 / 共 0 页",
            font=("SimHei", 10)
        )
        self.page_label.pack(side=tk.LEFT, padx=40)
        
        self.next_btn = tk.Button(
            self.control_frame, 
            text="下一页 (PageDown)", 
            command=self.next_page, 
            state=tk.DISABLED,
            padx=10,
            relief=tk.RAISED
        )
        self.next_btn.pack(side=tk.LEFT, padx=20)
        
        # 程序启动时检查是否有最近阅读记录，询问是否继续
        self.check_recent_history()

    # ------------------------------
    # 历史记录核心功能
    # ------------------------------
    def load_history(self):
        """加载历史记录（从JSON文件）"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # 若文件损坏，返回空列表
                return []
        return []

    def save_history(self):
        """保存历史记录（到JSON文件）"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.warning("警告", f"无法保存历史记录：{str(e)}")

    def update_history(self):
        """更新当前文件的历史记录（若已打开文件）"""
        if not self.current_file or not os.path.exists(self.current_file):
            return
        
        # 构建当前文件的记录信息
        record = {
            "path": self.current_file,
            "name": os.path.basename(self.current_file),
            "page": self.current_page,
            "font_size": self.font_size,
            "bg_name": self.current_bg_name,
            "last_read": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        # 移除已存在的相同文件记录（避免重复）
        self.history = [h for h in self.history if h["path"] != self.current_file]
        
        # 添加新记录到头部（最新的在最前）
        self.history.insert(0, record)
        
        # 限制历史记录数量
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
        
        # 保存并更新菜单
        self.save_history()
        self.update_history_menu()

    def update_history_menu(self):
        """更新历史记录菜单（动态显示最近文件）"""
        # 清空现有菜单
        self.history_submenu.delete(0, tk.END)
        
        if not self.history:
            self.history_submenu.add_command(label="无历史记录", state=tk.DISABLED)
            return
        
        # 添加历史记录条目
        for i, record in enumerate(self.history):
            # 显示格式：文件名（最后阅读时间）
            label = f"{record['name']} （{record['last_read']}）"
            self.history_submenu.add_command(
                label=label,
                command=lambda r=record: self.open_from_history(r)
            )
        
        # 添加清除历史记录功能
        self.history_submenu.add_separator()
        self.history_submenu.add_command(label="清除历史记录", command=self.clear_history)

    def open_from_history(self, record):
        """从历史记录打开文件并恢复状态"""
        file_path = record["path"]
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在：\n{file_path}\n已从历史记录中移除")
            # 移除无效记录
            self.history = [h for h in self.history if h["path"] != file_path]
            self.save_history()
            self.update_history_menu()
            return
        
        # 打开文件
        self.current_file = file_path
        self.load_file_content()
        
        # 恢复历史状态（页码、字体、背景）
        self.current_page = min(record["page"], self.total_pages - 1)  # 避免页码超出范围
        self.font_size = record["font_size"]
        self.set_background(record["bg_name"], from_history=True)  # 恢复背景
        
        # 更新显示
        self.text_widget.config(font=("SimHei", self.font_size))
        self.update_display()
        self.update_buttons()
        self.root.title(f"TXT阅读器 - {record['name']}")

    def check_recent_history(self):
        """程序启动时检查是否有最近记录，询问是否继续阅读"""
        if self.history:
            recent = self.history[0]
            if os.path.exists(recent["path"]):
                reply = messagebox.askyesno(
                    "继续阅读",
                    f"是否继续阅读：\n{recent['name']}\n最后阅读：{recent['last_read']}"
                )
                if reply:
                    self.open_from_history(recent)

    def clear_history(self):
        """清除所有历史记录"""
        if messagebox.askyesno("确认", "确定要清除所有历史记录吗？"):
            self.history = []
            self.save_history()
            self.update_history_menu()

    # ------------------------------
    # 文件操作与显示功能
    # ------------------------------
    def open_file(self):
        """打开新文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")],
            title="选择TXT文件"
        )
        
        if not file_path:
            return
        
        self.current_file = file_path
        self.load_file_content()
        
        # 重置状态（首次打开用默认值，若有历史记录会在open_from_history中覆盖）
        self.current_page = 0
        self.font_size = 12
        self.set_background("默认白", from_history=True)
        
        # 更新显示
        self.text_widget.config(font=("SimHei", self.font_size))
        self.update_display()
        self.update_buttons()
        self.root.title(f"TXT阅读器 - {os.path.basename(file_path)}")
        
        # 立即更新历史记录
        self.update_history()

    def load_file_content(self):
        """加载文件内容并分页"""
        encodings = ['utf-8', 'gbk', 'ansi', 'utf-16']
        content = None
        for encoding in encodings:
            try:
                with open(self.current_file, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except:
                continue
        
        if content is None:
            messagebox.showerror("错误", "无法读取文件，请检查文件格式或编码")
            self.current_file = None
            return
        
        # 处理换行符并分页
        lines = [line.rstrip('\r') for line in content.split('\n')]
        self.pages = []
        for i in range(0, len(lines), self.lines_per_page):
            page_content = '\n'.join(lines[i:i+self.lines_per_page])
            self.pages.append(page_content)
        self.total_pages = len(self.pages) if self.pages else 0

    def update_display(self):
        """更新文本显示"""
        if not self.pages:
            return
            
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, self.pages[self.current_page])
        self.text_widget.config(state=tk.DISABLED)
        self.page_label.config(text=f"第 {self.current_page + 1} 页 / 共 {self.total_pages} 页")
        
        # 每次更新显示后保存历史记录（确保阅读位置实时保存）
        self.update_history()

    def update_buttons(self):
        """更新翻页按钮状态"""
        if self.total_pages <= 1:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED)

    # ------------------------------
    # 翻页与视图调整功能
    # ------------------------------
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_display()
            self.update_buttons()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_display()
            self.update_buttons()

    def increase_font(self):
        if self.font_size < 32:
            self.font_size += 2
            self.text_widget.config(font=("SimHei", self.font_size))
            self.update_history()  # 保存字体大小变更

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 2
            self.text_widget.config(font=("SimHei", self.font_size))
            self.update_history()  # 保存字体大小变更

    def set_background(self, name, from_history=False):
        """设置背景色（from_history用于区分是否从历史记录恢复，避免重复更新）"""
        self.current_bg_name = name
        self.current_bg = self.bg_colors[name]
        self.text_widget.config(bg=self.current_bg)
        self.scrollbar.config(troughcolor=self.current_bg if name != "默认白" else "#EEEEEE")
        
        # 非历史记录恢复时，更新历史记录
        if not from_history:
            self.update_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = TxtReader(root)
    root.mainloop()