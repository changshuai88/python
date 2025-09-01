import os
import shutil
import wx
import wx.lib.newevent
from threading import Thread
import time

# 创建自定义事件用于更新UI
UpdateEvent, EVT_UPDATE = wx.lib.newevent.NewEvent()
FinishEvent, EVT_FINISH = wx.lib.newevent.NewEvent()

class ImageCopyFrame(wx.Frame):
    """主窗口类（修复查重逻辑）"""
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(700, 600))
        
        # 设置中文字体支持
        self.setup_fonts()
        
        # 创建主面板
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题
        title_label = wx.StaticText(main_panel, label="图片匹配复制工具（修复版）")
        font = title_label.GetFont()
        font.SetPointSize(16)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_label.SetFont(font)
        main_sizer.Add(title_label, 0, wx.ALL | wx.CENTER, 15)
        
        # 源文件夹选择
        source_box = wx.BoxSizer(wx.HORIZONTAL)
        source_label = wx.StaticText(main_panel, label="源图片文件夹:")
        source_box.Add(source_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.source_path = wx.TextCtrl(main_panel, style=wx.TE_READONLY)
        source_box.Add(self.source_path, 1, wx.ALIGN_CENTER_VERTICAL)
        
        source_btn = wx.Button(main_panel, label="浏览...")
        source_btn.Bind(wx.EVT_BUTTON, self.on_select_source)
        source_box.Add(source_btn, 0, wx.LEFT, 5)
        
        main_sizer.Add(source_box, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 匹配文件夹选择
        match_box = wx.BoxSizer(wx.HORIZONTAL)
        match_label = wx.StaticText(main_panel, label="用于匹配的文件夹:")
        match_box.Add(match_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.match_path = wx.TextCtrl(main_panel, style=wx.TE_READONLY)
        match_box.Add(self.match_path, 1, wx.ALIGN_CENTER_VERTICAL)
        
        match_btn = wx.Button(main_panel, label="浏览...")
        match_btn.Bind(wx.EVT_BUTTON, self.on_select_match)
        match_box.Add(match_btn, 0, wx.LEFT, 5)
        
        main_sizer.Add(match_box, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 目标文件夹选择
        dest_box = wx.BoxSizer(wx.HORIZONTAL)
        dest_label = wx.StaticText(main_panel, label="目标文件夹:")
        dest_box.Add(dest_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        
        self.dest_path = wx.TextCtrl(main_panel, style=wx.TE_READONLY)
        dest_box.Add(self.dest_path, 1, wx.ALIGN_CENTER_VERTICAL)
        
        dest_btn = wx.Button(main_panel, label="浏览...")
        dest_btn.Bind(wx.EVT_BUTTON, self.on_select_dest)
        dest_box.Add(dest_btn, 0, wx.LEFT, 5)
        
        main_sizer.Add(dest_box, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 处理按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.process_btn = wx.Button(main_panel, label="开始处理")
        self.process_btn.Bind(wx.EVT_BUTTON, self.on_process)
        font = self.process_btn.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.process_btn.SetFont(font)
        btn_sizer.Add(self.process_btn, 0, wx.ALL | wx.CENTER, 20)
        
        self.clear_btn = wx.Button(main_panel, label="清空日志")
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_log)
        btn_sizer.Add(self.clear_btn, 0, wx.ALL | wx.CENTER, 20)
        
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        
        # 日志区域
        log_box = wx.StaticBox(main_panel, label="处理日志（含查重细节）")
        log_sizer = wx.StaticBoxSizer(log_box, wx.VERTICAL)
        
        self.log_text = wx.TextCtrl(main_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.log_text.SetBackgroundColour(wx.WHITE)
        log_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(log_sizer, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 设置主面板布局
        main_panel.SetSizer(main_sizer)
        
        # 绑定自定义事件
        self.Bind(EVT_UPDATE, self.on_update)
        self.Bind(EVT_FINISH, self.on_finish)
        
        # 居中显示窗口
        self.Center()
        
        # 初始化路径（可选：设置默认路径）
        self.set_default_paths()

    def setup_fonts(self):
        """设置中文字体支持"""
        if wx.Platform == "__WXMSW__":
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "SimHei")
            self.SetFont(font)

    def set_default_paths(self):
        """设置默认路径（可修改）"""
        try:
            self.source_path.SetValue(r"F:\python\renameImage")
            self.match_path.SetValue(r"E:\work\卡特\卡特照片")
            self.dest_path.SetValue(r"E:\work\卡特\卡特照片\卡特照片2025")
        except:
            pass

    def on_select_source(self, event):
        """选择源文件夹"""
        dialog = wx.DirDialog(self, "选择源图片文件夹", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.source_path.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_select_match(self, event):
        """选择匹配文件夹"""
        dialog = wx.DirDialog(self, "选择用于匹配的文件夹", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.match_path.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_select_dest(self, event):
        """选择目标文件夹"""
        dialog = wx.DirDialog(self, "选择目标文件夹", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.dest_path.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_clear_log(self, event):
        """清空日志"""
        self.log_text.Clear()

    def log(self, message):
        """添加日志信息（带时间戳）"""
        log_msg = f"{time.strftime('%H:%M:%S')} - {message}\n"
        self.log_text.AppendText(log_msg)
        self.log_text.ShowPosition(self.log_text.GetLastPosition())  # 自动滚到底部

    def on_update(self, event):
        """更新日志事件处理"""
        self.log(event.message)

    def on_finish(self, event):
        """处理完成事件"""
        self.log("="*50)
        self.log(f"处理完成！共检查 {event.total} 张图片，成功复制 {event.copied} 张（无重复）")
        self.process_btn.Enable(True)
        wx.MessageBox(
            f"处理完成：\n共检查 {event.total} 张图片\n复制 {event.copied} 张缺失图片\n（已自动过滤匹配文件夹和目标文件夹的重复文件）",
            "处理完成",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_process(self, event):
        """开始处理（防重复点击）"""
        # 获取路径并验证
        source_dir = self.source_path.GetValue().strip()
        match_dir = self.match_path.GetValue().strip()
        dest_dir = self.dest_path.GetValue().strip()
        
        # 基础路径校验
        if not os.path.exists(source_dir):
            wx.MessageBox("请选择有效的源图片文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
        if not os.path.exists(match_dir):
            wx.MessageBox("请选择有效的匹配文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
        if not dest_dir:
            wx.MessageBox("请选择目标文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        # 禁用按钮+初始化日志
        self.process_btn.Disable()
        self.log("="*50)
        self.log("开始处理，正在初始化查重数据...")
        
        # 新线程执行（避免UI卡顿）
        thread = Thread(
            target=self.copy_missing_images,
            args=(source_dir, match_dir, dest_dir)
        )
        thread.daemon = True
        thread.start()

    def get_image_filenames(self, folder_path, log_prefix="匹配文件夹"):
        """
        修复核心：递归获取文件夹+子文件夹的图片文件名（含大小写不敏感处理）
        返回：{原始文件名: 小写文件名}（便于匹配）、总文件数
        """
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        image_files = {}  # 存储原始文件名与小写文件名的映射（防大小写问题）
        total_count = 0
        
        # 递归遍历所有子文件夹（修复原脚本只扫表层的问题）
        for root, _, files in os.walk(folder_path):
            # 记录当前扫描的子文件夹（便于日志排查）
            relative_path = os.path.relpath(root, folder_path)
            if relative_path == ".":
                self.log(f"[{log_prefix}] 扫描根目录: {root}")
            else:
                self.log(f"[{log_prefix}] 扫描子目录: {os.path.join(folder_path, relative_path)}")
            
            # 过滤图片文件
            for filename in files:
                # 排除隐藏文件（如Windows的Thumbs.db）
                if filename.startswith('.'):
                    continue
                # 检查文件扩展名（小写匹配，修复大小写问题）
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    lower_filename = filename.lower()  # 统一小写用于匹配
                    image_files[filename] = lower_filename
                    total_count += 1
        
        return image_files, total_count

    def copy_missing_images(self, source_dir, match_dir, dest_dir):
        """
        修复核心：
        1. 同时过滤「匹配文件夹」和「目标文件夹」的重复文件
        2. 递归处理源文件夹的子文件夹
        """
        # 1. 获取匹配文件夹的图片数据（用于查重）
        self.log("="*30)
        match_images, match_count = self.get_image_filenames(match_dir, log_prefix="匹配文件夹")
        self.log(f"[{match_count}张] 匹配文件夹图片已加载完成")
        
        # 2. 获取目标文件夹已有的图片数据（避免复制到目标后重复）
        self.log("="*30)
        dest_images, dest_count = self.get_image_filenames(dest_dir, log_prefix="目标文件夹")
        self.log(f"[{dest_count}张] 目标文件夹已有图片已加载完成")
        
        # 3. 确保目标文件夹存在
        try:
            os.makedirs(dest_dir, exist_ok=True)
            self.log(f"目标文件夹准备完成: {dest_dir}")
        except Exception as e:
            self.log(f"创建目标文件夹失败: {str(e)}")
            wx.PostEvent(self, FinishEvent(total=0, copied=0))
            return
        
        # 4. 递归处理源文件夹的所有图片（含子文件夹）
        self.log("="*30)
        self.log("开始扫描源文件夹并复制缺失图片...")
        total_files = 0
        copied_files = 0
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        
        for root, _, files in os.walk(source_dir):
            # 遍历源文件夹的每个文件
            for filename in files:
                # 排除隐藏文件和非图片
                if filename.startswith('.'):
                    continue
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in image_extensions:
                    continue
                
                total_files += 1
                source_file_path = os.path.join(root, filename)
                lower_filename = filename.lower()  # 统一小写用于匹配
                
                # 5. 查重判断：同时检查「匹配文件夹」和「目标文件夹」
                match_exists = any(lower_filename == v for v in match_images.values())
                dest_exists = any(lower_filename == v for v in dest_images.values())
                
                if match_exists:
                    self.log(f"[重复-匹配文件夹] 跳过: {filename}")
                elif dest_exists:
                    self.log(f"[重复-目标文件夹] 跳过: {filename}")
                else:
                    # 复制文件（保留元数据）
                    dest_file_path = os.path.join(dest_dir, filename)
                    try:
                        shutil.copy2(source_file_path, dest_file_path)
                        self.log(f"[成功复制] {filename} → {os.path.relpath(dest_file_path, dest_dir)}")
                        copied_files += 1
                        # 更新目标文件夹的图片列表（避免后续重复判断）
                        dest_images[filename] = lower_filename
                    except Exception as e:
                        self.log(f"[复制失败] {filename}: {str(e)}")
        
        # 6. 发送处理完成事件
        wx.PostEvent(self, FinishEvent(total=total_files, copied=copied_files))


class ImageCopyApp(wx.App):
    """应用程序类"""
    def OnInit(self):
        frame = ImageCopyFrame(None, title="图片匹配复制工具（修复查重版）")
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = ImageCopyApp()
    app.MainLoop()