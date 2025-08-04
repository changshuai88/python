import os
import shutil
import wx
from PIL import Image
from pyzbar.pyzbar import decode

class QRImageRenamer:
    """二维码图片处理核心类"""
    def __init__(self):
        pass

    def scan_qr_code(self, image_path):
        """扫描图片中的二维码并返回解码后的字符串"""
        try:
            # 读取图片
            image = Image.open(image_path)

            # 解码二维码
            decoded_objects = decode(image)
            if decoded_objects:
                # 返回第一个二维码的解码结果
                return decoded_objects[0].data.decode('utf-8')
            else:
                return "未在图片中找到二维码。"
        except Exception as e:
            print(f"扫描二维码时出错: {e}")
            return f"扫描二维码时出错: {str(e)}"

    def rename_and_move_image(self, qr_image_path, target_image_path, output_folder):
        """扫描二维码图片，获取字符串，用该字符串重命名目标图片并移动到指定文件夹"""
        # 扫描二维码获取字符串
        qr_string = self.scan_qr_code(qr_image_path)
        if qr_string and qr_string not in ["未在图片中找到二维码。", "扫描二维码时出错:"]:
            # 获取目标图片的文件扩展名
            file_extension = os.path.splitext(target_image_path)[1].lower()
            # 生成新的文件名
            new_filename = f"{qr_string}{file_extension}"
            # 生成新的文件路径
            new_file_path = os.path.join(output_folder, new_filename)
            
            # 处理文件名重复的情况
            counter = 1
            while os.path.exists(new_file_path):
                new_filename = f"{qr_string}_{counter}{file_extension}"
                new_file_path = os.path.join(output_folder, new_filename)
                counter += 1
                
            try:
                # 确保输出文件夹存在
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                # 复制并重命名文件
                shutil.copy2(target_image_path, new_file_path)
                return f"图片已重命名并保存到:\n{new_file_path}"
            except Exception as e:
                return f"重命名和移动图片时出错: {e}"
        else:
            return f"二维码处理失败: {qr_string}"


class FileDropTarget(wx.FileDropTarget):
    """文件拖放目标类"""
    def __init__(self, window, is_folder=False, file_types=None, callback=None):
        wx.FileDropTarget.__init__(self)
        self.window = window
        self.is_folder = is_folder  # 是否接受文件夹
        self.file_types = file_types or ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        self.callback = callback  # 拖放完成后的回调函数

    def OnDropFiles(self, x, y, filenames):
        """处理拖放的文件"""
        if not filenames:
            return False
            
        # 只处理第一个文件/文件夹
        file_path = filenames[0]
        
        # 检查是否为文件夹或符合类型的文件
        if self.is_folder:
            if os.path.isdir(file_path):
                self.window.set_path(file_path)
                if self.callback:
                    self.callback(file_path)
                return True
        else:
            if any(file_path.lower().endswith(ext) for ext in self.file_types):
                self.window.set_path(file_path)
                if self.callback:
                    self.callback(file_path)
                return True
                
        # 如果不符合条件，显示错误信息
        if self.is_folder:
            wx.MessageBox("请拖放一个文件夹", "错误", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox(f"请拖放图片文件 ({', '.join(self.file_types)})", "错误", wx.OK | wx.ICON_ERROR)
            
        return False


class DropZone(wx.Panel):
    """拖放区域面板"""
    def __init__(self, parent, label_text, is_folder=False, file_types=None, callback=None, default_path=None):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SUNKEN)
        
        self.path = ""
        self.is_folder = is_folder
        self.default_path = default_path  # 默认路径
        
        # 设置面板背景色
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # 创建布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 提示标签
        self.label = wx.StaticText(self, label=label_text)
        sizer.Add(self.label, 0, wx.ALL | wx.CENTER, 10)
        
        # 文件路径显示
        self.path_text = wx.TextCtrl(self, style=wx.TE_READONLY | wx.HSCROLL)
        sizer.Add(self.path_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
        # 设置拖放目标
        drop_target = FileDropTarget(self, is_folder, file_types, callback)
        self.SetDropTarget(drop_target)
        
        # 绑定鼠标进入/离开事件，用于视觉反馈
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        
        # 如果有默认路径，设置默认路径
        if self.default_path:
            self.set_path(self.default_path, is_default=True)

    def on_enter(self, event):
        """鼠标进入区域时改变背景色"""
        self.SetBackgroundColour(wx.Colour(224, 224, 224))
        self.Refresh()
        event.Skip()

    def on_leave(self, event):
        """鼠标离开区域时恢复背景色"""
        if self.path:
            self.SetBackgroundColour(wx.Colour(208, 240, 208))  # 已拖放文件时的颜色
        else:
            self.SetBackgroundColour(wx.Colour(240, 240, 240))  # 默认颜色
        self.Refresh()
        event.Skip()

    def set_path(self, path, is_default=False):
        """设置文件路径并更新显示"""
        self.path = path
        # 显示简短路径
        display_path = path if len(path) < 50 else "..." + path[-47:]
        # 如果是默认路径，添加标识
        if is_default:
            display_path += " (默认)"
        self.path_text.SetValue(display_path)
        # 改变背景色表示已设置路径
        self.SetBackgroundColour(wx.Colour(208, 240, 208))
        self.Refresh()

    def get_path(self):
        """获取文件路径"""
        # 如果路径为空且有默认路径，返回默认路径
        return self.path if self.path else self.default_path

    def clear(self):
        """清空路径和显示，恢复默认路径（如果有）"""
        self.path = ""
        if self.default_path:
            self.set_path(self.default_path, is_default=True)
        else:
            self.path_text.SetValue("")
            self.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.Refresh()


class QRImageRenamerFrame(wx.Frame):
    """主窗口类"""
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(700, 600))
        
        self.renamer = QRImageRenamer()
        # 设置默认输出文件夹
        self.default_output_folder = os.path.abspath("./renameImage")
        # 确保默认文件夹存在
        self.ensure_default_folder_exists()
        
        # 设置中文字体支持
        self.setup_fonts()
        
        # 创建主面板
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题
        title_label = wx.StaticText(main_panel, label="二维码图片重命名工具")
        font = title_label.GetFont()
        font.SetPointSize(16)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title_label.SetFont(font)
        main_sizer.Add(title_label, 0, wx.ALL | wx.CENTER, 15)
        
        # 提示信息
        hint_label = wx.StaticText(
            main_panel, 
            label="请将文件拖放到相应区域，支持图片文件和文件夹的拖放"
        )
        hint_font = hint_label.GetFont()
        hint_font.SetPointSize(9)
        hint_label.SetFont(hint_font)
        hint_label.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(hint_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # 二维码图片拖放区域
        qr_label = wx.StaticText(main_panel, label="1. 拖放包含二维码的图片:")
        main_sizer.Add(qr_label, 0, wx.LEFT | wx.TOP, 10)
        
        self.qr_drop_zone = DropZone(
            main_panel, 
            "将二维码图片拖放到此处",
            callback=self.on_qr_dropped
        )
        main_sizer.Add(self.qr_drop_zone, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 目标图片拖放区域
        target_label = wx.StaticText(main_panel, label="2. 拖放需要重命名的图片:")
        main_sizer.Add(target_label, 0, wx.LEFT | wx.TOP, 15)
        
        self.target_drop_zone = DropZone(
            main_panel, 
            "将需要重命名的图片拖放到此处",
            callback=self.on_target_dropped
        )
        main_sizer.Add(self.target_drop_zone, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 输出文件夹拖放区域
        output_label = wx.StaticText(main_panel, label="3. 拖放输出文件夹:")
        main_sizer.Add(output_label, 0, wx.LEFT | wx.TOP, 15)
        
        self.output_drop_zone = DropZone(
            main_panel, 
            "将输出文件夹拖放到此处（默认: ./renameImage）",
            is_folder=True,
            callback=self.on_output_dropped,
            default_path=self.default_output_folder  # 设置默认路径
        )
        main_sizer.Add(self.output_drop_zone, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 处理按钮
        process_btn = wx.Button(main_panel, label="处理图片")
        process_btn.Bind(wx.EVT_BUTTON, self.on_process)
        font = process_btn.GetFont()
        font.SetPointSize(10)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        process_btn.SetFont(font)
        main_sizer.Add(process_btn, 0, wx.ALL | wx.CENTER, 20)
        
        # 图片预览区域
        preview_box = wx.StaticBox(main_panel, label="图片预览")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.HORIZONTAL)
        
        # 二维码图片预览
        self.qr_preview = wx.StaticBitmap(main_panel)
        self.qr_preview_label = wx.StaticText(main_panel, label="二维码图片预览")
        qr_preview_sizer = wx.BoxSizer(wx.VERTICAL)
        qr_preview_sizer.Add(self.qr_preview_label, 0, wx.CENTER | wx.BOTTOM, 5)
        qr_preview_sizer.Add(self.qr_preview, 1, wx.EXPAND | wx.ALL, 5)
        preview_sizer.Add(qr_preview_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # 目标图片预览
        self.target_preview = wx.StaticBitmap(main_panel)
        self.target_preview_label = wx.StaticText(main_panel, label="目标图片预览")
        target_preview_sizer = wx.BoxSizer(wx.VERTICAL)
        target_preview_sizer.Add(self.target_preview_label, 0, wx.CENTER | wx.BOTTOM, 5)
        target_preview_sizer.Add(self.target_preview, 1, wx.EXPAND | wx.ALL, 5)
        preview_sizer.Add(target_preview_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(preview_sizer, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # 设置主面板布局
        main_panel.SetSizer(main_sizer)
        
        # 居中显示窗口
        self.Center()

    def ensure_default_folder_exists(self):
        """确保默认输出文件夹存在"""
        if not os.path.exists(self.default_output_folder):
            try:
                os.makedirs(self.default_output_folder)
                print(f"已创建默认输出文件夹: {self.default_output_folder}")
            except Exception as e:
                wx.MessageBox(
                    f"无法创建默认输出文件夹: {str(e)}\n请手动创建或拖放其他文件夹", 
                    "警告", 
                    wx.OK | wx.ICON_WARNING
                )

    def setup_fonts(self):
        """设置中文字体支持"""
        if wx.Platform == "__WXMSW__":
            # Windows系统设置
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "SimHei")
            self.SetFont(font)

    def on_qr_dropped(self, file_path):
        """处理二维码图片拖放"""
        self.preview_image(file_path, self.qr_preview)

    def on_target_dropped(self, file_path):
        """处理目标图片拖放"""
        self.preview_image(file_path, self.target_preview)

    def on_output_dropped(self, folder_path):
        """处理输出文件夹拖放"""
        pass  # 仅需要设置路径，由DropZone内部处理

    def preview_image(self, file_path, preview_ctrl):
        """预览图片"""
        try:
            # 打开图片并调整大小以适应预览
            image = Image.open(file_path)
            image.thumbnail((300, 200))  # 限制预览图大小
            
            # 转换为wxPython可用的图像格式
            wx_image = wx.Image(image.width, image.height)
            wx_image.SetData(image.convert("RGB").tobytes())
            wx_bitmap = wx.Bitmap(wx_image)
            
            # 更新预览控件
            preview_ctrl.SetBitmap(wx_bitmap)
            preview_ctrl.Refresh()
        except Exception as e:
            wx.MessageBox(f"无法预览图片: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)

    def on_process(self, event):
        """处理图片重命名"""
        qr_path = self.qr_drop_zone.get_path()
        target_path = self.target_drop_zone.get_path()
        output_path = self.output_drop_zone.get_path()  # 会自动获取默认路径
        
        # 验证输入
        if not qr_path:
            wx.MessageBox("请拖放包含二维码的图片", "错误", wx.OK | wx.ICON_ERROR)
            return
            
        if not target_path:
            wx.MessageBox("请拖放需要重命名的图片", "错误", wx.OK | wx.ICON_ERROR)
            return
            
        if not output_path or not os.path.exists(output_path):
            wx.MessageBox("输出文件夹不存在，请拖放有效的文件夹", "错误", wx.OK | wx.ICON_ERROR)
            return
            
        # 处理图片
        result = self.renamer.rename_and_move_image(qr_path, target_path, output_path)
        wx.MessageBox(result, "处理结果", wx.OK | wx.ICON_INFORMATION)
        
        # 清空输入，准备下一次操作
        self.qr_drop_zone.clear()
        self.target_drop_zone.clear()
        self.output_drop_zone.clear()  # 清空后会恢复默认路径
        self.qr_preview.SetBitmap(wx.Bitmap())
        self.target_preview.SetBitmap(wx.Bitmap())
        self.qr_preview_label.SetLabel("二维码图片预览")
        self.target_preview_label.SetLabel("目标图片预览")


class QRImageRenamerApp(wx.App):
    """应用程序类"""
    def OnInit(self):
        frame = QRImageRenamerFrame(None, title="二维码图片重命名工具")
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = QRImageRenamerApp()
    app.MainLoop()
