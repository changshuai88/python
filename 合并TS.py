<<<<<<< HEAD
import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
import logging

class TSFileMergerApp:
    """TS文件合并工具的GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TS文件合并工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCheckbutton", font=("SimHei", 10))
        self.style.configure("Treeview", font=("SimHei", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入区域
        self._create_input_frame()
        
        # 创建输出区域
        self._create_output_frame()
        
        # 创建文件列表区域
        self._create_file_list_frame()
        
        # 创建状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建按钮区域
        self._create_button_frame()
        
        # 用于线程间通信的队列
        self.queue = queue.Queue()
        
        # 当前TS文件列表
        self.ts_files = []
        
        # 配置日志
        self._configure_logging()
        
    def _configure_logging(self):
        """配置日志系统"""
        self.logger = logging.getLogger("TSFileMerger")
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler("ts_merger.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器并添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到logger
        self.logger.addHandler(file_handler)
        
    def _create_input_frame(self):
        """创建输入区域"""
        self.input_frame = ttk.LabelFrame(self.main_frame, text="输入设置", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # 选择TS文件目录
        ttk.Label(self.input_frame, text="TS文件目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ts_dir_var = tk.StringVar()
        self.ts_dir_entry = ttk.Entry(self.input_frame, textvariable=self.ts_dir_var, width=50)
        self.ts_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_btn = ttk.Button(self.input_frame, text="浏览...", command=self.browse_ts_directory)
        self.browse_btn.grid(row=0, column=2, padx=5)
        
        # 排序模式
        ttk.Label(self.input_frame, text="排序模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sort_pattern_var = tk.StringVar(value=r'(\d+)')
        self.sort_pattern_entry = ttk.Entry(self.input_frame, textvariable=self.sort_pattern_var, width=30)
        self.sort_pattern_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.input_frame, text="(正则表达式，用于提取排序数字)").grid(row=1, column=2, sticky=tk.W, pady=5)
        
    def _create_output_frame(self):
        """创建输出区域"""
        self.output_frame = ttk.LabelFrame(self.main_frame, text="输出设置", padding="10")
        self.output_frame.pack(fill=tk.X, pady=5)
        
        # 选择输出文件
        ttk.Label(self.output_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar()
        self.output_file_entry = ttk.Entry(self.output_frame, textvariable=self.output_file_var, width=50)
        self.output_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_output_btn = ttk.Button(self.output_frame, text="浏览...", command=self.browse_output_file)
        self.browse_output_btn.grid(row=0, column=2, padx=5)
        
        # 合并方法
        ttk.Label(self.output_frame, text="合并方法:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.merge_method_var = tk.StringVar(value="ffmpeg")
        self.ffmpeg_radio = ttk.Radiobutton(self.output_frame, text="FFmpeg (推荐)", variable=self.merge_method_var, value="ffmpeg")
        self.ffmpeg_radio.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.direct_radio = ttk.Radiobutton(self.output_frame, text="直接合并 (快速但可能有兼容性问题)", variable=self.merge_method_var, value="direct")
        self.direct_radio.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # FFmpeg选项
        self.ffmpeg_options_frame = ttk.Frame(self.output_frame)
        self.ffmpeg_options_frame.grid(row=1, column=2, rowspan=2, sticky=(tk.W, tk.N), padx=10)
        
        self.copy_mode_var = tk.BooleanVar(value=True)
        self.copy_mode_check = ttk.Checkbutton(self.ffmpeg_options_frame, text="不重新编码 (更快)", variable=self.copy_mode_var)
        self.copy_mode_check.pack(anchor=tk.W, pady=2)
        
    def _create_file_list_frame(self):
        """创建文件列表区域"""
        self.file_list_frame = ttk.LabelFrame(self.main_frame, text="TS文件列表", padding="10")
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建文件列表树视图
        columns = ("序号", "文件名", "大小")
        self.file_tree = ttk.Treeview(self.file_list_frame, columns=columns, show="headings")
        for col in columns:
            self.file_tree.heading(col, text=col)
            width = 100 if col == "序号" else 300 if col == "文件名" else 100
            self.file_tree.column(col, width=width, anchor=tk.W)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.file_list_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
    def _create_button_frame(self):
        """创建按钮区域"""
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.pack(fill=tk.X, pady=5)
        
        self.load_button = ttk.Button(self.button_frame, text="加载TS文件", command=self.load_ts_files)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.load_button.configure(state=tk.DISABLED)  # 初始禁用
        
        self.merge_button = ttk.Button(self.button_frame, text="开始合并", command=self.start_merge)
        self.merge_button.pack(side=tk.LEFT, padx=5)
        self.merge_button.configure(state=tk.DISABLED)  # 初始禁用
        
        self.quit_button = ttk.Button(self.button_frame, text="退出", command=self.root.quit)
        self.quit_button.pack(side=tk.RIGHT, padx=5)
        
    def browse_ts_directory(self):
        """浏览并选择TS文件目录"""
        directory = filedialog.askdirectory(title="选择TS文件目录")
        if directory:
            self.ts_dir_var.set(directory)
            self.output_file_var.set(os.path.join(directory, "merged.ts"))
            self.load_button.configure(state=tk.NORMAL)  # 启用加载按钮
            self.logger.info(f"选择TS文件目录: {directory}")
    
    def browse_output_file(self):
        """浏览并选择输出文件"""
        filetypes = [("视频文件", "*.mp4;*.ts;*.mkv"), ("所有文件", "*.*")]
        filename = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".mp4",
            filetypes=filetypes
        )
        if filename:
            self.output_file_var.set(filename)
            self.logger.info(f"选择输出文件: {filename}")
    
    def load_ts_files(self):
        """加载并显示TS文件列表"""
        ts_dir = self.ts_dir_var.get()
        self.logger.info(f"尝试加载TS文件，目录: {ts_dir}")
        
        if not ts_dir or not os.path.exists(ts_dir):
            messagebox.showerror("错误", "请选择有效的TS文件目录")
            self.logger.error(f"无效的目录: {ts_dir}")
            return
        
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 获取并排序TS文件
        sort_pattern = self.sort_pattern_var.get()
        self.ts_files = self.get_sorted_ts_files(ts_dir, sort_pattern=sort_pattern)
        
        if not self.ts_files:
            messagebox.showinfo("提示", f"在目录 {ts_dir} 中没有找到TS文件")
            self.logger.warning(f"在目录 {ts_dir} 中未找到TS文件")
            self.merge_button.configure(state=tk.DISABLED)  # 禁用合并按钮
            return
        
        # 显示文件列表
        for i, ts_file in enumerate(self.ts_files, 1):
            try:
                size = os.path.getsize(ts_file)
                size_str = self.format_size(size)
            except OSError:
                size_str = "未知"
            self.file_tree.insert("", tk.END, values=(i, os.path.basename(ts_file), size_str))
        
        self.status_var.set(f"已加载 {len(self.ts_files)} 个TS文件")
        self.merge_button.configure(state=tk.NORMAL)  # 启用合并按钮
        self.logger.info(f"成功加载 {len(self.ts_files)} 个TS文件")
    
    def format_size(self, size_bytes):
        """将字节大小转换为人类可读的格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def get_sorted_ts_files(self, directory, sort_pattern=r'(\d+)'):
        """获取目录中按特定模式和排序规则排列的TS文件列表"""
        if not os.path.exists(directory):
            return []
        
        # 获取所有匹配的TS文件
        ts_files = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.lower().endswith('.ts')
        ]
        
        self.logger.info(f"在目录 {directory} 中找到 {len(ts_files)} 个TS文件")
        
        # 定义排序函数
        def sort_key(filename):
            """从文件名中提取数字进行排序"""
            match = re.search(sort_pattern, os.path.basename(filename))
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    self.logger.warning(f"无法从文件名 {os.path.basename(filename)} 中提取排序数字")
                    pass
            return filename  # 如果没有匹配到数字，则按原文件名排序
        
        # 排序文件
        ts_files.sort(key=sort_key)
        
        self.logger.info(f"TS文件排序完成，排序模式: {sort_pattern}")
        for file in ts_files:
            self.logger.debug(f"排序后的文件: {os.path.basename(file)}")
            
        return ts_files
    
    def start_merge(self):
        """开始合并TS文件"""
        if not self.ts_files:
            messagebox.showerror("错误", "没有TS文件可供合并，请先加载TS文件")
            return
        
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.logger.info(f"创建输出目录: {output_dir}")
            except OSError as e:
                messagebox.showerror("错误", f"无法创建输出目录: {e}")
                self.logger.error(f"创建输出目录失败: {e}")
                return
        
        # 禁用按钮防止重复点击
        for button in self.button_frame.winfo_children():
            button.configure(state=tk.DISABLED)
        
        self.status_var.set("正在合并...")
        self.logger.info(f"开始合并TS文件，输出路径: {output_file}，合并方法: {self.merge_method_var.get()}")
        
        # 在新线程中执行合并操作
        merge_thread = threading.Thread(target=self.perform_merge, daemon=True)
        merge_thread.start()
        
        # 开始轮询队列以获取状态更新
        self.root.after(100, self.check_queue)
    
    def perform_merge(self):
        """执行合并操作"""
        try:
            output_file = self.output_file_var.get()
            method = self.merge_method_var.get()
            
            if method == "ffmpeg":
                success = self.merge_ts_files_with_ffmpeg(
                    self.ts_files, 
                    output_file, 
                    use_copy=self.copy_mode_var.get()
                )
            else:
                success = self.merge_ts_files_directly(
                    self.ts_files, 
                    output_file
                )
            
            if success:
                self.queue.put(("success", f"合并成功，文件已保存到: {output_file}"))
                self.logger.info(f"合并成功，输出文件: {output_file}")
            else:
                self.queue.put(("error", "合并失败"))
                self.logger.error("合并失败")
                
        except Exception as e:
            self.queue.put(("error", f"发生错误: {str(e)}"))
            self.logger.exception(f"合并过程中发生异常: {str(e)}")
        finally:
            # 重新启用按钮
            self.queue.put(("enable_buttons",))
    
    def merge_ts_files_with_ffmpeg(self, ts_files, output_file, use_copy=True):
        """
        使用ffmpeg合并TS文件
        
        参数:
        ts_files: 按顺序排列的TS文件列表
        output_file: 输出文件路径
        use_copy: 是否使用-copy选项(不重新编码，速度快)
        """
        if not ts_files:
            self.queue.put(("message", "没有TS文件可供合并"))
            self.logger.warning("没有TS文件可供合并")
            return False
        
        # 检查FFmpeg是否可用
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.queue.put(("error", "未找到FFmpeg。请确保FFmpeg已安装并添加到系统PATH中。"))
            self.logger.error("未找到FFmpeg")
            return False
        
        # 生成ffmpeg命令
        cmd = ["ffmpeg", "-y"]
        
        # 添加所有输入文件
        for ts_file in ts_files:
            cmd.extend(["-i", ts_file])
        
        # 使用concat demuxer方法
        cmd.extend(["-filter_complex", f"concat=n={len(ts_files)}:v=1:a=1"])
        
        # 如果使用copy模式，则不重新编码
        if use_copy:
            cmd.extend(["-c", "copy"])
        
        # 指定输出文件
        cmd.append(output_file)
        
        self.queue.put(("message", f"执行命令: {' '.join(cmd)}"))
        self.logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
        
        try:
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                bufsize=1,
                universal_newlines=True
            )
            self.queue.put(("message", f"ffmpeg输出: {result.stdout}"))
            self.logger.debug(f"FFmpeg标准输出: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            self.queue.put(("message", f"合并失败: {e.stderr}"))
            self.logger.error(f"FFmpeg执行失败: {e.stderr}")
            return False
    
    def merge_ts_files_directly(self, ts_files, output_file):
        """
        直接合并TS文件(简单连接，可能在某些播放器中无法正常工作)
        
        参数:
        ts_files: 按顺序排列的TS文件列表
        output_file: 输出文件路径
        """
        if not ts_files:
            self.queue.put(("message", "没有TS文件可供合并"))
            self.logger.warning("没有TS文件可供合并")
            return False
        
        total_files = len(ts_files)
        
        try:
            with open(output_file, 'wb') as outfile:
                for i, ts_file in enumerate(ts_files):
                    self.queue.put(("message", f"正在合并文件 {i+1}/{total_files}: {os.path.basename(ts_file)}"))
                    self.logger.info(f"正在合并文件 {i+1}/{total_files}: {os.path.basename(ts_file)}")
                    with open(ts_file, 'rb') as infile:
                        # 分块读取，避免大文件内存问题
                        while chunk := infile.read(1024*1024):  # 1MB块
                            outfile.write(chunk)
            return True
        except Exception as e:
            self.queue.put(("message", f"直接合并失败: {e}"))
            self.logger.error(f"直接合并失败: {e}")
            return False
    
    def check_queue(self):
        """检查队列中的消息"""
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                if msg[0] == "message":
                    self.status_var.set(msg[1])
                elif msg[0] == "success":
                    self.status_var.set(msg[1])
                    messagebox.showinfo("成功", msg[1])
                elif msg[0] == "error":
                    self.status_var.set(msg[1])
                    messagebox.showerror("错误", msg[1])
                elif msg[0] == "enable_buttons":
                    # 启用除退出按钮外的所有按钮
                    for button in self.button_frame.winfo_children():
                        if button != self.quit_button:
                            button.configure(state=tk.NORMAL)
            except queue.Empty:
                pass
        
        # 继续轮询
        if any(t.is_alive() for t in threading.enumerate() if t != threading.current_thread()):
            self.root.after(100, self.check_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = TSFileMergerApp(root)
=======
import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
import logging

class TSFileMergerApp:
    """TS文件合并工具的GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TS文件合并工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TCheckbutton", font=("SimHei", 10))
        self.style.configure("Treeview", font=("SimHei", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入区域
        self._create_input_frame()
        
        # 创建输出区域
        self._create_output_frame()
        
        # 创建文件列表区域
        self._create_file_list_frame()
        
        # 创建状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建按钮区域
        self._create_button_frame()
        
        # 用于线程间通信的队列
        self.queue = queue.Queue()
        
        # 当前TS文件列表
        self.ts_files = []
        
        # 配置日志
        self._configure_logging()
        
    def _configure_logging(self):
        """配置日志系统"""
        self.logger = logging.getLogger("TSFileMerger")
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler("ts_merger.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器并添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到logger
        self.logger.addHandler(file_handler)
        
    def _create_input_frame(self):
        """创建输入区域"""
        self.input_frame = ttk.LabelFrame(self.main_frame, text="输入设置", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # 选择TS文件目录
        ttk.Label(self.input_frame, text="TS文件目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ts_dir_var = tk.StringVar()
        self.ts_dir_entry = ttk.Entry(self.input_frame, textvariable=self.ts_dir_var, width=50)
        self.ts_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_btn = ttk.Button(self.input_frame, text="浏览...", command=self.browse_ts_directory)
        self.browse_btn.grid(row=0, column=2, padx=5)
        
        # 排序模式
        ttk.Label(self.input_frame, text="排序模式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sort_pattern_var = tk.StringVar(value=r'(\d+)')
        self.sort_pattern_entry = ttk.Entry(self.input_frame, textvariable=self.sort_pattern_var, width=30)
        self.sort_pattern_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.input_frame, text="(正则表达式，用于提取排序数字)").grid(row=1, column=2, sticky=tk.W, pady=5)
        
    def _create_output_frame(self):
        """创建输出区域"""
        self.output_frame = ttk.LabelFrame(self.main_frame, text="输出设置", padding="10")
        self.output_frame.pack(fill=tk.X, pady=5)
        
        # 选择输出文件
        ttk.Label(self.output_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar()
        self.output_file_entry = ttk.Entry(self.output_frame, textvariable=self.output_file_var, width=50)
        self.output_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.browse_output_btn = ttk.Button(self.output_frame, text="浏览...", command=self.browse_output_file)
        self.browse_output_btn.grid(row=0, column=2, padx=5)
        
        # 合并方法
        ttk.Label(self.output_frame, text="合并方法:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.merge_method_var = tk.StringVar(value="ffmpeg")
        self.ffmpeg_radio = ttk.Radiobutton(self.output_frame, text="FFmpeg (推荐)", variable=self.merge_method_var, value="ffmpeg")
        self.ffmpeg_radio.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.direct_radio = ttk.Radiobutton(self.output_frame, text="直接合并 (快速但可能有兼容性问题)", variable=self.merge_method_var, value="direct")
        self.direct_radio.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # FFmpeg选项
        self.ffmpeg_options_frame = ttk.Frame(self.output_frame)
        self.ffmpeg_options_frame.grid(row=1, column=2, rowspan=2, sticky=(tk.W, tk.N), padx=10)
        
        self.copy_mode_var = tk.BooleanVar(value=True)
        self.copy_mode_check = ttk.Checkbutton(self.ffmpeg_options_frame, text="不重新编码 (更快)", variable=self.copy_mode_var)
        self.copy_mode_check.pack(anchor=tk.W, pady=2)
        
    def _create_file_list_frame(self):
        """创建文件列表区域"""
        self.file_list_frame = ttk.LabelFrame(self.main_frame, text="TS文件列表", padding="10")
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建文件列表树视图
        columns = ("序号", "文件名", "大小")
        self.file_tree = ttk.Treeview(self.file_list_frame, columns=columns, show="headings")
        for col in columns:
            self.file_tree.heading(col, text=col)
            width = 100 if col == "序号" else 300 if col == "文件名" else 100
            self.file_tree.column(col, width=width, anchor=tk.W)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(self.file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.file_list_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
    def _create_button_frame(self):
        """创建按钮区域"""
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.pack(fill=tk.X, pady=5)
        
        self.load_button = ttk.Button(self.button_frame, text="加载TS文件", command=self.load_ts_files)
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.load_button.configure(state=tk.DISABLED)  # 初始禁用
        
        self.merge_button = ttk.Button(self.button_frame, text="开始合并", command=self.start_merge)
        self.merge_button.pack(side=tk.LEFT, padx=5)
        self.merge_button.configure(state=tk.DISABLED)  # 初始禁用
        
        self.quit_button = ttk.Button(self.button_frame, text="退出", command=self.root.quit)
        self.quit_button.pack(side=tk.RIGHT, padx=5)
        
    def browse_ts_directory(self):
        """浏览并选择TS文件目录"""
        directory = filedialog.askdirectory(title="选择TS文件目录")
        if directory:
            self.ts_dir_var.set(directory)
            self.output_file_var.set(os.path.join(directory, "merged.ts"))
            self.load_button.configure(state=tk.NORMAL)  # 启用加载按钮
            self.logger.info(f"选择TS文件目录: {directory}")
    
    def browse_output_file(self):
        """浏览并选择输出文件"""
        filetypes = [("视频文件", "*.mp4;*.ts;*.mkv"), ("所有文件", "*.*")]
        filename = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".mp4",
            filetypes=filetypes
        )
        if filename:
            self.output_file_var.set(filename)
            self.logger.info(f"选择输出文件: {filename}")
    
    def load_ts_files(self):
        """加载并显示TS文件列表"""
        ts_dir = self.ts_dir_var.get()
        self.logger.info(f"尝试加载TS文件，目录: {ts_dir}")
        
        if not ts_dir or not os.path.exists(ts_dir):
            messagebox.showerror("错误", "请选择有效的TS文件目录")
            self.logger.error(f"无效的目录: {ts_dir}")
            return
        
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 获取并排序TS文件
        sort_pattern = self.sort_pattern_var.get()
        self.ts_files = self.get_sorted_ts_files(ts_dir, sort_pattern=sort_pattern)
        
        if not self.ts_files:
            messagebox.showinfo("提示", f"在目录 {ts_dir} 中没有找到TS文件")
            self.logger.warning(f"在目录 {ts_dir} 中未找到TS文件")
            self.merge_button.configure(state=tk.DISABLED)  # 禁用合并按钮
            return
        
        # 显示文件列表
        for i, ts_file in enumerate(self.ts_files, 1):
            try:
                size = os.path.getsize(ts_file)
                size_str = self.format_size(size)
            except OSError:
                size_str = "未知"
            self.file_tree.insert("", tk.END, values=(i, os.path.basename(ts_file), size_str))
        
        self.status_var.set(f"已加载 {len(self.ts_files)} 个TS文件")
        self.merge_button.configure(state=tk.NORMAL)  # 启用合并按钮
        self.logger.info(f"成功加载 {len(self.ts_files)} 个TS文件")
    
    def format_size(self, size_bytes):
        """将字节大小转换为人类可读的格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def get_sorted_ts_files(self, directory, sort_pattern=r'(\d+)'):
        """获取目录中按特定模式和排序规则排列的TS文件列表"""
        if not os.path.exists(directory):
            return []
        
        # 获取所有匹配的TS文件
        ts_files = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.lower().endswith('.ts')
        ]
        
        self.logger.info(f"在目录 {directory} 中找到 {len(ts_files)} 个TS文件")
        
        # 定义排序函数
        def sort_key(filename):
            """从文件名中提取数字进行排序"""
            match = re.search(sort_pattern, os.path.basename(filename))
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    self.logger.warning(f"无法从文件名 {os.path.basename(filename)} 中提取排序数字")
                    pass
            return filename  # 如果没有匹配到数字，则按原文件名排序
        
        # 排序文件
        ts_files.sort(key=sort_key)
        
        self.logger.info(f"TS文件排序完成，排序模式: {sort_pattern}")
        for file in ts_files:
            self.logger.debug(f"排序后的文件: {os.path.basename(file)}")
            
        return ts_files
    
    def start_merge(self):
        """开始合并TS文件"""
        if not self.ts_files:
            messagebox.showerror("错误", "没有TS文件可供合并，请先加载TS文件")
            return
        
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.logger.info(f"创建输出目录: {output_dir}")
            except OSError as e:
                messagebox.showerror("错误", f"无法创建输出目录: {e}")
                self.logger.error(f"创建输出目录失败: {e}")
                return
        
        # 禁用按钮防止重复点击
        for button in self.button_frame.winfo_children():
            button.configure(state=tk.DISABLED)
        
        self.status_var.set("正在合并...")
        self.logger.info(f"开始合并TS文件，输出路径: {output_file}，合并方法: {self.merge_method_var.get()}")
        
        # 在新线程中执行合并操作
        merge_thread = threading.Thread(target=self.perform_merge, daemon=True)
        merge_thread.start()
        
        # 开始轮询队列以获取状态更新
        self.root.after(100, self.check_queue)
    
    def perform_merge(self):
        """执行合并操作"""
        try:
            output_file = self.output_file_var.get()
            method = self.merge_method_var.get()
            
            if method == "ffmpeg":
                success = self.merge_ts_files_with_ffmpeg(
                    self.ts_files, 
                    output_file, 
                    use_copy=self.copy_mode_var.get()
                )
            else:
                success = self.merge_ts_files_directly(
                    self.ts_files, 
                    output_file
                )
            
            if success:
                self.queue.put(("success", f"合并成功，文件已保存到: {output_file}"))
                self.logger.info(f"合并成功，输出文件: {output_file}")
            else:
                self.queue.put(("error", "合并失败"))
                self.logger.error("合并失败")
                
        except Exception as e:
            self.queue.put(("error", f"发生错误: {str(e)}"))
            self.logger.exception(f"合并过程中发生异常: {str(e)}")
        finally:
            # 重新启用按钮
            self.queue.put(("enable_buttons",))
    
    def merge_ts_files_with_ffmpeg(self, ts_files, output_file, use_copy=True):
        """
        使用ffmpeg合并TS文件
        
        参数:
        ts_files: 按顺序排列的TS文件列表
        output_file: 输出文件路径
        use_copy: 是否使用-copy选项(不重新编码，速度快)
        """
        if not ts_files:
            self.queue.put(("message", "没有TS文件可供合并"))
            self.logger.warning("没有TS文件可供合并")
            return False
        
        # 检查FFmpeg是否可用
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.queue.put(("error", "未找到FFmpeg。请确保FFmpeg已安装并添加到系统PATH中。"))
            self.logger.error("未找到FFmpeg")
            return False
        
        # 生成ffmpeg命令
        cmd = ["ffmpeg", "-y"]
        
        # 添加所有输入文件
        for ts_file in ts_files:
            cmd.extend(["-i", ts_file])
        
        # 使用concat demuxer方法
        cmd.extend(["-filter_complex", f"concat=n={len(ts_files)}:v=1:a=1"])
        
        # 如果使用copy模式，则不重新编码
        if use_copy:
            cmd.extend(["-c", "copy"])
        
        # 指定输出文件
        cmd.append(output_file)
        
        self.queue.put(("message", f"执行命令: {' '.join(cmd)}"))
        self.logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
        
        try:
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                bufsize=1,
                universal_newlines=True
            )
            self.queue.put(("message", f"ffmpeg输出: {result.stdout}"))
            self.logger.debug(f"FFmpeg标准输出: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            self.queue.put(("message", f"合并失败: {e.stderr}"))
            self.logger.error(f"FFmpeg执行失败: {e.stderr}")
            return False
    
    def merge_ts_files_directly(self, ts_files, output_file):
        """
        直接合并TS文件(简单连接，可能在某些播放器中无法正常工作)
        
        参数:
        ts_files: 按顺序排列的TS文件列表
        output_file: 输出文件路径
        """
        if not ts_files:
            self.queue.put(("message", "没有TS文件可供合并"))
            self.logger.warning("没有TS文件可供合并")
            return False
        
        total_files = len(ts_files)
        
        try:
            with open(output_file, 'wb') as outfile:
                for i, ts_file in enumerate(ts_files):
                    self.queue.put(("message", f"正在合并文件 {i+1}/{total_files}: {os.path.basename(ts_file)}"))
                    self.logger.info(f"正在合并文件 {i+1}/{total_files}: {os.path.basename(ts_file)}")
                    with open(ts_file, 'rb') as infile:
                        # 分块读取，避免大文件内存问题
                        while chunk := infile.read(1024*1024):  # 1MB块
                            outfile.write(chunk)
            return True
        except Exception as e:
            self.queue.put(("message", f"直接合并失败: {e}"))
            self.logger.error(f"直接合并失败: {e}")
            return False
    
    def check_queue(self):
        """检查队列中的消息"""
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                if msg[0] == "message":
                    self.status_var.set(msg[1])
                elif msg[0] == "success":
                    self.status_var.set(msg[1])
                    messagebox.showinfo("成功", msg[1])
                elif msg[0] == "error":
                    self.status_var.set(msg[1])
                    messagebox.showerror("错误", msg[1])
                elif msg[0] == "enable_buttons":
                    # 启用除退出按钮外的所有按钮
                    for button in self.button_frame.winfo_children():
                        if button != self.quit_button:
                            button.configure(state=tk.NORMAL)
            except queue.Empty:
                pass
        
        # 继续轮询
        if any(t.is_alive() for t in threading.enumerate() if t != threading.current_thread()):
            self.root.after(100, self.check_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = TSFileMergerApp(root)
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
    root.mainloop()