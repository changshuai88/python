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
    """主窗口类"""
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(700, 600))
        
        # 设置中文字体支持
        self.setup_fonts()
        
        # 创建主面板
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题
        title_label = wx.StaticText(main_panel, label="图片匹配复制工具")
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
        log_box = wx.StaticBox(main_panel, label="处理日志")
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
            # Windows系统设置
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "SimHei")
            self.SetFont(font)

    def set_default_paths(self):
        """设置默认路径（可选）"""
        try:
            # 可以根据需要修改默认路径
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
        """添加日志信息"""
        self.log_text.AppendText(f"{time.strftime('%H:%M:%S')} - {message}\n")
        # 自动滚动到底部
        self.log_text.ShowPosition(self.log_text.GetLastPosition())

    def on_update(self, event):
        """更新日志事件处理"""
        self.log(event.message)

    def on_finish(self, event):
        """处理完成事件"""
        self.log("处理完成！")
        self.process_btn.Enable(True)
        wx.MessageBox(
            f"处理完成：共检查 {event.total} 张图片，复制了 {event.copied} 张缺失图片",
            "处理完成",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_process(self, event):
        """开始处理"""
        # 获取文件夹路径
        source_dir = self.source_path.GetValue().strip()
        match_dir = self.match_path.GetValue().strip()
        dest_dir = self.dest_path.GetValue().strip()
        
        # 验证路径
        if not source_dir or not os.path.exists(source_dir):
            wx.MessageBox("请选择有效的源图片文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
            
        if not match_dir or not os.path.exists(match_dir):
            wx.MessageBox("请选择有效的匹配文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
            
        if not dest_dir:
            wx.MessageBox("请选择目标文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        # 禁用处理按钮，防止重复点击
        self.process_btn.Disable()
        self.log("开始处理...")
        
        # 在新线程中执行处理，避免UI卡顿
        thread = Thread(
            target=self.copy_missing_images,
            args=(source_dir, match_dir, dest_dir)
        )
        thread.daemon = True
        thread.start()

    def get_image_filenames(self, folder_path):
        """获取指定文件夹中所有图片的文件名（不含路径）"""
        # 定义常见图片文件扩展名
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        
        # 存储文件名的集合（集合查找效率更高）
        image_files = set()
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            wx.PostEvent(self, UpdateEvent(message=f"警告：文件夹 {folder_path} 不存在"))
            return image_files
        
        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            # 拼接完整路径
            file_path = os.path.join(folder_path, filename)
            
            # 只处理文件（不处理文件夹）且是图片格式
            if os.path.isfile(file_path) and filename.lower().endswith(image_extensions):
                # 添加文件名到集合（不含路径）
                image_files.add(filename)
        
        return image_files

    def copy_missing_images(self, source_dir, match_dir, dest_dir):
        """复制源文件夹中在匹配文件夹不存在的图片到目标文件夹"""
        # 获取匹配文件夹中的图片文件名集合
        wx.PostEvent(self, UpdateEvent(message=f"正在分析匹配文件夹 {match_dir}..."))
        match_images = self.get_image_filenames(match_dir)
        wx.PostEvent(self, UpdateEvent(message=f"在匹配文件夹中找到 {len(match_images)} 张图片"))
        
        # 确保目标文件夹存在
        try:
            os.makedirs(dest_dir, exist_ok=True)
            wx.PostEvent(self, UpdateEvent(message=f"目标文件夹：{dest_dir}（若不存在已自动创建）"))
        except Exception as e:
            wx.PostEvent(self, UpdateEvent(message=f"创建目标文件夹失败：{str(e)}"))
            wx.PostEvent(self, FinishEvent(total=0, copied=0))
            return
        
        # 定义图片文件扩展名
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
        
        # 统计变量
        total_files = 0
        copied_files = 0
        
        # 遍历源文件夹中的文件
        for filename in os.listdir(source_dir):
            # 拼接完整路径
            source_path = os.path.join(source_dir, filename)
            
            # 只处理文件（不处理文件夹）且是图片格式
            if os.path.isfile(source_path) and filename.lower().endswith(image_extensions):
                total_files += 1
                
                # 检查文件名是否在匹配文件夹中存在
                if filename not in match_images:
                    # 目标路径
                    dest_path = os.path.join(dest_dir, filename)
                    
                    # 复制文件
                    try:
                        shutil.copy2(source_path, dest_path)  # copy2保留文件元数据
                        wx.PostEvent(self, UpdateEvent(message=f"已复制：{filename}"))
                        copied_files += 1
                    except Exception as e:
                        wx.PostEvent(self, UpdateEvent(message=f"复制失败 {filename}：{str(e)}"))
        
        # 发送处理完成事件
        wx.PostEvent(self, FinishEvent(total=total_files, copied=copied_files))


class ImageCopyApp(wx.App):
    """应用程序类"""
    def OnInit(self):
        frame = ImageCopyFrame(None, title="图片匹配复制工具")
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = ImageCopyApp()
    app.MainLoop()
