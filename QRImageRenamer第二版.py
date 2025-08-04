import cv2
from pyzbar.pyzbar import decode
import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD


class QRImageRenamer:
    def __init__(self):
        pass

    def scan_qr_code(self, image_path):
        try:
            image = Image.open(image_path)
            decoded_objects = decode(image)
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    qr_data = re.findall(r'[^\u4e00-\u9fa5?]', qr_data)
                    qr_data = ''.join(qr_data)
                    print(qr_data)
                    return qr_data
            else:
                return "未在图片中找到二维码。"
        except Exception as e:
            print(f"扫描二维码时出错: {e}")
            return None

    def rename_and_move_image(self, qr_image_path, target_image_path, output_folder):
        qr_string = self.scan_qr_code(qr_image_path)
        if qr_string:
            file_extension = os.path.splitext(target_image_path)[1]
            new_filename = f"{qr_string}{file_extension}"
            new_file_path = os.path.join(output_folder, new_filename)
            try:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                shutil.copy2(target_image_path, new_file_path)
                return f"图片已重命名并保存到: {new_file_path}"
            except Exception as e:
                return f"重命名和移动图片时出错: {e}"
        else:
            return "未找到二维码或扫描出错。"


class QRImageRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("二维码图片重命名工具")
        self.renamer = QRImageRenamer()

        self.qr_image_path = tk.StringVar()
        self.target_image_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        default_path = "./renameImage"
        self.output_folder.set(default_path)

        # 二维码图片展示框
        tk.Label(root, text="二维码图片:").grid(row=0, column=0, padx=5, pady=5)
        self.qr_image_label = tk.Label(root, width=200, height=100, relief=tk.SUNKEN, borderwidth=1, highlightthickness=1)
        self.qr_image_label.grid(row=0, column=1, padx=5, pady=5)
        self.qr_image_label.drop_target_register(DND_FILES)
        self.qr_image_label.dnd_bind('<<Drop>>', self.on_drop_qr)

        # 目标图片展示框
        tk.Label(root, text="目标图片:").grid(row=1, column=0, padx=5, pady=5)
        self.target_image_label = tk.Label(root, width=200, height=100, relief=tk.SUNKEN, borderwidth=1, highlightthickness=1)
        self.target_image_label.grid(row=1, column=1, padx=5, pady=5)
        self.target_image_label.drop_target_register(DND_FILES)
        self.target_image_label.dnd_bind('<<Drop>>', self.on_drop_target)

        tk.Label(root, text="输出文件夹路径:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.output_folder, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(root, text="选择文件夹", command=self.select_output_folder).grid(row=2, column=2, padx=5, pady=5)

        tk.Button(root, text="处理图片", command=self.process_images).grid(row=3, column=1, padx=10, pady=20)

        tk.Button(root, text="再次启动", command=self.restart_script).grid(row=4, column=1, padx=10, pady=20)

    def on_drop_qr(self, event):
        file_path = event.data.strip('{}')
        if file_path and file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.qr_image_path.set(file_path)
            self.show_image(self.qr_image_label, file_path)

    def on_drop_target(self, event):
        file_path = event.data.strip('{}')
        if file_path and file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.target_image_path.set(file_path)
            self.show_image(self.target_image_label, file_path)

    def show_image(self, label, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            print(f"显示图片时出错: {e}")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder.set(folder_path)

    def process_images(self):
        qr_path = self.qr_image_path.get()
        target_path = self.target_image_path.get()
        output_path = self.output_folder.get()
        default_path = "./renameImage"
        output_path = output_path if output_path else default_path
        if not qr_path or not target_path or not output_path:
            messagebox.showerror("错误", "请确保选择了所有必要的文件和文件夹。")
            return

        result = self.renamer.rename_and_move_image(qr_path, target_path, output_path)
        messagebox.showinfo("处理结果", result)
        self.reset_ui()

    def reset_ui(self):
        self.qr_image_label.config(image=None)
        self.qr_image_label.image = None
        self.target_image_label.config(image=None)
        self.target_image_label.image = None
        self.qr_image_path.set("")
        self.target_image_path.set("")

    def restart_script(self):
        self.reset_ui()


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.geometry("600x800")
    app = QRImageRenamerGUI(root)
    root.mainloop()