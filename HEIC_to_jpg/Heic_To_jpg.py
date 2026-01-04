import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from PIL import Image
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

class HEIC2JPGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HEIC批量转换为JPG工具 - 可视化版")
        self.root.geometry("800x600")  # 窗口大小
        self.root.resizable(True, True)

        # 初始化变量
        self.source_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.recursive = tk.BooleanVar(value=False)
        self.quality = tk.StringVar(value="95")
        self.conversion_thread = None
        self.is_running = False

        # 构建UI
        self._build_ui()
        # 检查依赖
        self._check_dependencies()

    def _build_ui(self):
        """构建UI界面"""
        # 1. 源文件夹选择区域
        frame_source = ttk.LabelFrame(self.root, text="源文件夹（HEIC文件所在）")
        frame_source.pack(fill="x", padx=10, pady=5)

        ttk.Entry(frame_source, textvariable=self.source_dir, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(frame_source, text="浏览", command=self._select_source_dir).pack(side="right", padx=5, pady=5)

        # 2. 输出文件夹选择区域
        frame_output = ttk.LabelFrame(self.root, text="输出文件夹（JPG保存位置）")
        frame_output.pack(fill="x", padx=10, pady=5)

        ttk.Entry(frame_output, textvariable=self.output_dir, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(frame_output, text="浏览", command=self._select_output_dir).pack(side="right", padx=5, pady=5)

        # 3. 转换选项区域
        frame_options = ttk.LabelFrame(self.root, text="转换选项")
        frame_options.pack(fill="x", padx=10, pady=5)

        # 递归选项
        ttk.Checkbutton(frame_options, text="递归处理子文件夹", variable=self.recursive).pack(side="left", padx=10, pady=5)

        # 质量设置
        ttk.Label(frame_options, text="JPG质量（1-100）：").pack(side="left", padx=10, pady=5)
        quality_entry = ttk.Entry(frame_options, textvariable=self.quality, width=10)
        quality_entry.pack(side="left", padx=5, pady=5)
        quality_entry.insert(0, "95")

        # 4. 操作按钮区域
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        self.start_btn = ttk.Button(frame_buttons, text="开始转换", command=self._start_conversion)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(frame_buttons, text="停止转换", command=self._stop_conversion, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        ttk.Button(frame_buttons, text="清空日志", command=self._clear_log).pack(side="right", padx=5)

        # 5. 进度条区域
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # 6. 日志显示区域
        frame_log = ttk.LabelFrame(self.root, text="转换日志")
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _check_dependencies(self):
        """检查依赖并提示"""
        if not HEIF_SUPPORT:
            self._log("❌ 缺少pillow-heif库，请先安装：pip install pillow pillow-heif", "error")
            self.start_btn.config(state="disabled")
        else:
            self._log("✅ 依赖检查通过，可正常转换HEIC文件", "info")

    def _select_source_dir(self):
        """选择源文件夹"""
        dir_path = filedialog.askdirectory(title="选择包含HEIC文件的文件夹")
        if dir_path:
            self.source_dir.set(dir_path)
            # 若未选输出文件夹，默认设为源文件夹下的JPG_Output
            if not self.output_dir.get():
                default_output = os.path.join(dir_path, "JPG_Output")
                self.output_dir.set(default_output)

    def _select_output_dir(self):
        """选择输出文件夹"""
        dir_path = filedialog.askdirectory(title="选择JPG文件保存的文件夹")
        if dir_path:
            self.output_dir.set(dir_path)

    def _log(self, msg, level="info"):
        """日志输出到UI文本框"""
        self.log_text.config(state="normal")
        color = {"info": "black", "error": "red", "success": "green"}[level]
        self.log_text.insert(tk.END, f"{msg}\n", level)
        self.log_text.tag_configure(level, foreground=color)
        self.log_text.see(tk.END)  # 自动滚动到最后
        self.log_text.config(state="disabled")
        self.root.update_idletasks()  # 刷新UI

    def _clear_log(self):
        """清空日志"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def _validate_inputs(self):
        """验证输入参数"""
        # 检查源文件夹
        if not self.source_dir.get() or not os.path.isdir(self.source_dir.get()):
            messagebox.showerror("错误", "请选择有效的源文件夹！")
            return False

        # 检查输出文件夹（不存在则创建）
        if not self.output_dir.get():
            messagebox.showerror("错误", "请选择有效的输出文件夹！")
            return False
        os.makedirs(self.output_dir.get(), exist_ok=True)

        # 检查质量参数
        try:
            quality = int(self.quality.get())
            if not 1 <= quality <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "JPG质量必须是1-100之间的数字！")
            return False

        return True

    def _get_heic_files(self):
        """获取所有待转换的HEIC文件"""
        heic_suffixes = (".heic", ".heif", ".Heic", ".Heif", ".HEIC", ".HEIF")
        heic_files = []
        source_dir = self.source_dir.get()

        if self.recursive.get():
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith(heic_suffixes):
                        heic_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(source_dir):
                file_path = os.path.join(source_dir, file)
                if os.path.isfile(file_path) and file.endswith(heic_suffixes):
                    heic_files.append(file_path)

        return heic_files

    def _convert_heic_to_jpg(self, input_path, quality):
        """单个HEIC文件转换"""
        # 构建输出路径：保持原文件目录结构（相对源文件夹）
        rel_path = os.path.relpath(input_path, self.source_dir.get())
        output_path = os.path.join(self.output_dir.get(), os.path.splitext(rel_path)[0] + ".jpg")
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 检查是否覆盖
        if os.path.exists(output_path):
            # UI线程弹窗确认（需用after回到主线程）
            overwrite = [False]
            def ask_overwrite():
                overwrite[0] = messagebox.askyesno("确认", f"文件 {os.path.basename(output_path)} 已存在，是否覆盖？")
            self.root.after(0, ask_overwrite)
            # 等待弹窗结果
            while not overwrite[0] and not self.is_running:
                pass
            if not overwrite[0]:
                return False, "用户取消覆盖"

        try:
            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            return True, f"转换成功：{os.path.basename(input_path)} → {os.path.basename(output_path)}"
        except Exception as e:
            return False, f"转换失败：{str(e)}"

    def _conversion_worker(self):
        """转换线程的工作函数"""
        # 初始化统计
        total = 0
        success = 0
        fail = 0
        fail_list = []

        try:
            # 1. 获取待转换文件
            self._log("🔍 正在扫描HEIC文件...", "info")
            heic_files = self._get_heic_files()
            total = len(heic_files)
            if total == 0:
                self._log("📭 未找到任何HEIC/HEIF格式文件！", "info")
                return

            self._log(f"🚀 共找到 {total} 个HEIC文件，开始转换...", "info")
            self.progress["maximum"] = total
            self.progress["value"] = 0

            # 2. 批量转换
            quality = int(self.quality.get())
            for idx, file_path in enumerate(heic_files):
                if not self.is_running:
                    break
                # 转换单个文件
                res, msg = self._convert_heic_to_jpg(file_path, quality)
                if res:
                    success += 1
                    self._log(msg, "success")
                else:
                    fail += 1
                    fail_msg = f"❌ {os.path.basename(file_path)}：{msg}"
                    fail_list.append(fail_msg)
                    self._log(fail_msg, "error")
                # 更新进度
                self.progress["value"] = idx + 1
                self.root.update_idletasks()

            # 3. 输出统计结果
            self._log("\n" + "="*50, "info")
            self._log(f"📊 转换完成！总文件数：{total} | 成功：{success} | 失败：{fail}", "info")
            if fail_list:
                self._log("❌ 失败文件列表：", "error")
                for msg in fail_list:
                    self._log(msg, "error")
            self._log("🎉 任务结束！", "info")

        except Exception as e:
            self._log(f"💥 转换过程出错：{str(e)}", "error")
        finally:
            # 恢复UI状态
            self.is_running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.progress["value"] = 0

    def _start_conversion(self):
        """开始转换"""
        # 验证输入
        if not self._validate_inputs():
            return

        # 检查是否已在运行
        if self.is_running:
            messagebox.showwarning("提示", "转换任务已在运行中！")
            return

        # 初始化状态
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._clear_log()
        self._log("📋 转换参数确认：", "info")
        self._log(f"   源文件夹：{self.source_dir.get()}", "info")
        self._log(f"   输出文件夹：{self.output_dir.get()}", "info")
        self._log(f"   递归子文件夹：{self.recursive.get()}", "info")
        self._log(f"   JPG质量：{self.quality.get()}", "info")

        # 启动转换线程
        self.conversion_thread = threading.Thread(target=self._conversion_worker, daemon=True)
        self.conversion_thread.start()

    def _stop_conversion(self):
        """停止转换"""
        if self.is_running:
            self.is_running = False
            self._log("🛑 用户请求停止转换，正在结束任务...", "info")
            self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = HEIC2JPGConverter(root)
    root.mainloop()