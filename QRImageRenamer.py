import cv2
from pyzbar.pyzbar import decode
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
'''
第一个选框里面放有二维码的照片
第二个框放需要重命名的照片
第三个选择存放重命名之后的照片文件夹


'''

class QRImageRenamer:
    def __init__(self):
        pass

    def scan_qr_code(self, image_path):
        """
        扫描图片中的二维码并返回解码后的字符串
        :param image_path: 图片文件的路径
        :return: 二维码解码后的字符串，如果未找到二维码则返回 None
        """
        try:
            # 读取图片
            # image = cv2.imread(image_path)
            image = Image.open(image_path)

            # 解码二维码
            decoded_objects = decode(image)
            if decoded_objects:
                # 返回第一个二维码的解码结果
                # return decoded_objects[0].data.decode('utf-8')
            # return None
                for obj in decoded_objects:
                # 获取二维码中的数据并解码为字符串
                    qr_data = obj.data.decode('utf-8')
                    return qr_data
            else:
                return "未在图片中找到二维码。"
        except Exception as e:
            print(f"扫描二维码时出错: {e}")
            return None

    def rename_and_move_image(self, qr_image_path, target_image_path, output_folder):
        """
        扫描二维码图片，获取字符串，用该字符串重命名目标图片并移动到指定文件夹
        :param qr_image_path: 包含二维码的图片文件路径
        :param target_image_path: 要重命名的目标图片文件路径
        :param output_folder: 重命名后的图片要保存的文件夹路径
        """
        # 扫描二维码获取字符串
        qr_string = self.scan_qr_code(qr_image_path)
        if qr_string:
            # 获取目标图片的文件扩展名
            file_extension = os.path.splitext(target_image_path)[1]
            # 生成新的文件名
            new_filename = f"{qr_string}{file_extension}"
            # 生成新的文件路径
            new_file_path = os.path.join(output_folder, new_filename)
            try:
                # 确保输出文件夹存在
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                # 复制并重命名文件
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

        # 变量用于存储文件路径
        self.qr_image_path = tk.StringVar()
        self.target_image_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        default_path = "./renameImage"
        self.output_folder.set(default_path)

        # 创建标签和输入框
        tk.Label(root, text="二维码图片路径:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(root, textvariable=self.qr_image_path, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(root, text="选择文件", command=self.select_qr_image).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(root, text="目标图片路径:").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(root, textvariable=self.target_image_path, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(root, text="选择文件", command=self.select_target_image).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(root, text="输出文件夹路径:").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(root, textvariable=self.output_folder, width=50).grid(row=2, column=1, padx=10, pady=5)
        tk.Button(root, text="选择文件夹", command=self.select_output_folder).grid(row=2, column=2, padx=10, pady=5)

        # 处理按钮
        tk.Button(root, text="处理图片", command=self.process_images).grid(row=3, column=1, padx=10, pady=20)

    def select_qr_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.png")])
        if file_path:
            self.qr_image_path.set(file_path)

    def select_target_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.png")])
        if file_path:
            self.target_image_path.set(file_path)

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

        # 清空输入框内容
        self.qr_image_path.set("")
        self.target_image_path.set("")
        # self.output_folder.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRImageRenamerGUI(root)
    root.mainloop()