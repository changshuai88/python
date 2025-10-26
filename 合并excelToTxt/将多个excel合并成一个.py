import os
import pylightxl as xl
import pandas as pd
# import pylightxl as xl
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


class ExcelToTxtMerger:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel转TXT合并工具")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        self.default_output = r"D:\sales\sales.txt"
        self.column_sep = "    |    "
        
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))

        ttk.Label(
            root, 
            text="功能：读取Excel文件数据并追加到TXT，格式说明：\n"
                 "1. 每个文件的来源信息单独作为首行\n"
                 "2. 列数据用 '    |    ' 分隔（|左右各4个空格）\n"
                 "3. 每行数据之间用 ------- 分割\n"
                 "4. 自动过滤无数据的空行",
            foreground="#0066cc"
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        ttk.Label(root, text="Excel文件所在文件夹:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.folder_path = tk.StringVar()
        ttk.Entry(root, textvariable=self.folder_path, width=60).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(root, text="浏览...", command=self.select_folder).grid(row=1, column=2, padx=10, pady=10)

        ttk.Label(root, text="合并后TXT保存路径:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.output_path = tk.StringVar(value=self.default_output)
        ttk.Entry(root, textvariable=self.output_path, width=60).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(root, text="选择保存位置", command=self.select_output).grid(row=2, column=2, padx=10, pady=10)

        ttk.Button(
            root, 
            text="开始处理", 
            command=self.start_merging
        ).grid(row=3, column=0, columnspan=3, pady=10)

        ttk.Label(root, text="处理进度:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        ttk.Label(root, text="处理日志:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.log_text = tk.Text(root, height=12, width=75)
        self.log_text.grid(row=7, column=0, columnspan=3, padx=10, pady=5)
        self.log_text.config(state="disabled")

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择包含Excel文件的文件夹（支持.xls和.xlsx）")
        if folder:
            self.folder_path.set(folder)

    def select_output(self):
        default_dir = os.path.dirname(self.default_output)
        if not os.path.exists(default_dir):
            os.makedirs(default_dir, exist_ok=True)
        
        file = filedialog.asksaveasfilename(
            title="保存合并结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialdir=default_dir,
            initialfile="sales.txt"
        )
        if file:
            self.output_path.set(file)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def read_excel_with_pylightxl(self, file_path):
        """使用pylightxl读取.xls文件，转换为DataFrame"""
        try:
            wb = xl.readxl(file_path)
            sheet = wb.ws(ws=wb.ws_names[0])  # 读取第一个工作表
            data = sheet.rows
            df = pd.DataFrame(data[1:], columns=data[0])  # 假设第一行为表头
            return df
        except Exception as e:
            self.log(f"使用pylightxl读取{os.path.basename(file_path)}失败：{str(e)}")
            return None

    def read_excel_with_pandas(self, file_path):
        """使用pandas读取.xlsx文件"""
        try:
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='openpyxl')
            return df
        except Exception as e:
            self.log(f"使用pandas读取{os.path.basename(file_path)}失败：{str(e)}")
            return None

    def process_excel_data(self, df):
        df = df.fillna("")
        data_rows = df.values.tolist()
        filtered_rows = []
        for row in data_rows:
            if any(str(cell).strip() != "" for cell in row):
                filtered_rows.append(row)
        return filtered_rows

    def merge_to_txt(self):
        input_folder = self.folder_path.get()
        output_file = self.output_path.get()

        if not input_folder:
            messagebox.showerror("错误", "请选择Excel文件所在文件夹")
            self.progress.stop()
            return

        if not os.path.exists(input_folder):
            messagebox.showerror("错误", f"文件夹不存在：{input_folder}")
            self.progress.stop()
            return

        excel_files = []
        for filename in os.listdir(input_folder):
            if (filename.endswith('.xlsx') or filename.endswith('.xls')) and not filename.startswith('~$'):
                excel_files.append(os.path.join(input_folder, filename))

        if not excel_files:
            messagebox.showinfo("提示", "未找到可合并的Excel文件（.xls或.xlsx）")
            self.progress.stop()
            return

        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.log(f"已自动创建输出文件夹：{output_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"创建文件夹失败：{str(e)}")
                self.progress.stop()
                return

        self.log(f"找到 {len(excel_files)} 个Excel文件，开始读取数据...")
        total_rows = 0
        error_files = []

        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                for i, file_path in enumerate(excel_files):
                    filename = os.path.basename(file_path)
                    try:
                        if file_path.endswith('.xls'):
                            df = self.read_excel_with_pylightxl(file_path)
                        else:
                            df = self.read_excel_with_pandas(file_path)

                        if df is None:
                            error_files.append(f"{filename}（读取失败）")
                            continue

                        data_rows = self.process_excel_data(df)
                        rows_count = len(data_rows)
                        total_rows += rows_count

                        if rows_count == 0:
                            self.log(f"处理完成：{filename}（无有效数据行）")
                            continue

                        f.write(f"【来源文件：{filename}】\n")
                        for idx, row in enumerate(data_rows):
                            line = self.column_sep.join(map(str, row)) + '\n'
                            f.write(line)
                            if idx != rows_count - 1:
                                f.write("-------\n")

                        self.log(f"成功处理：{filename}（{rows_count}行有效数据）")
                    except Exception as e:
                        error_files.append(f"{filename}（错误：{str(e)}）")
                        self.log(f"处理失败：{filename} - {str(e)}")
                    
                    self.progress["value"] = (i + 1) / len(excel_files) * 100
                    self.root.update_idletasks()

            report = [
                f"处理完成！共处理 {len(excel_files)} 个文件",
                f"成功追加 {total_rows} 行有效数据到：{output_file}"
            ]
            if error_files:
                report.append(f"处理错误的文件：{len(error_files)} 个")
            
            self.log("\n" + "\n".join(report))
            messagebox.showinfo("成功", "\n".join(report))

        except Exception as e:
            self.log(f"写入TXT文件失败：{str(e)}")
            messagebox.showerror("错误", f"写入TXT文件失败：{str(e)}")

        if error_files:
            err_msg = f"处理失败的文件列表：\n" + "\n".join(error_files)
            self.log(f"\n{err_msg}")
            messagebox.showwarning("部分文件处理失败", err_msg)

        self.progress.stop()

    def start_merging(self):
        self.progress["value"] = 0
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

        merge_thread = threading.Thread(target=self.merge_to_txt)
        merge_thread.daemon = True
        merge_thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelToTxtMerger(root)
    root.mainloop()