import pandas as pd
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

def filter_and_copy_excel(input_file, output_file, column='L', value=1, header=True):
    """
    从Excel文件中筛选特定列等于特定值的行，并保存到新文件
    
    参数:
        input_file (str): 输入Excel文件路径
        output_file (str): 输出Excel文件路径
        column (str): 筛选列名，默认为 'L'
        value (any): 筛选值，默认为 1
        header (bool): 输入文件是否包含表头，默认为 True
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(input_file, header=0 if header else None)
        
        # 检查筛选列是否存在
        if header and column not in df.columns:
            print(f"错误: 文件中未找到 '{column}' 列。")
            return False
        
        # 根据是否有表头调整列索引
        col_idx = column if header else ord(column.upper()) - 65  # 字母转列索引
        
        # 筛选符合条件的行
        filtered_df = df[df[col_idx] == value]
        
        # 检查是否有匹配的行
        if filtered_df.empty:
            print(f"提示: 在 '{column}' 列中未找到值为 {value} 的行。")
            return True
        
        # 创建输出目录（如果不存在）
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存筛选结果
        filtered_df.to_excel(output_file, index=False, header=header)
        print(f"成功: 已将 {len(filtered_df)} 行复制到 {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{input_file}'")
        return False
    except KeyError as e:
        print(f"错误: 指定列 '{column}' 不存在: {e}")
        return False
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
        return False

def select_file(title, filetypes=[("Excel files", "*.xlsx;*.xls")]):
    """创建Tkinter文件选择对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 置顶窗口
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )
    root.destroy()
    return file_path

def select_save_path(title, defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")]):
    """创建Tkinter文件保存对话框"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 置顶窗口
    
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes
    )
    root.destroy()
    return file_path

def interactive_mode():
    """交互式模式，通过对话框选择文件"""
    print("=== Excel 筛选工具 - 交互式模式 ===")
    
    # 选择输入文件
    print("请选择输入Excel文件...")
    input_file = select_file("选择输入Excel文件")
    
    if not input_file:
        print("未选择文件，程序退出。")
        return False
    
    # 选择输出文件
    print("请选择输出Excel文件保存位置...")
    output_file = select_save_path("选择输出Excel文件位置")
    
    if not output_file:
        print("未选择保存位置，程序退出。")
        return False
    
    # 获取筛选条件
    column = input("请输入筛选列名 (默认为 L): ").strip() or 'L'
    
    # 尝试将输入的值转换为整数，失败则保持为字符串
    value_input = input("请输入筛选值 (默认为 1): ").strip()
    value = 1 if not value_input else value_input
    try:
        value = int(value)
    except ValueError:
        pass  # 保持为字符串
    
    # 获取表头选项
    header_input = input("输入文件是否包含表头? (Y/n): ").strip().lower()
    header = header_input != 'n'
    
    # 执行筛选
    return filter_and_copy_excel(
        input_file=input_file,
        output_file=output_file,
        column=column,
        value=value,
        header=header
    )

if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        parser = argparse.ArgumentParser(description='从Excel文件中筛选特定列等于特定值的行，并保存到新文件')
        parser.add_argument('-i', '--input', help='输入Excel文件路径')
        parser.add_argument('-o', '--output', help='输出Excel文件路径')
        parser.add_argument('-c', '--column', default='L', help='筛选列名，默认为 L')
        parser.add_argument('-v', '--value', type=int, default=1, help='筛选值，默认为 1')
        parser.add_argument('--no-header', action='store_false', dest='header', 
                            help='指定输入文件不包含表头')
        args = parser.parse_args()
        
        # 如果没有提供必要参数，进入交互式模式
        if not args.input or not args.output:
            interactive_mode()
        else:
            filter_and_copy_excel(
                input_file=args.input,
                output_file=args.output,
                column=args.column,
                value=args.value,
                header=args.header
            )
    else:
        # 无参数时直接进入交互式模式
        interactive_mode()    