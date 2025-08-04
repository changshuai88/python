import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

class CatPartViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("CAT零件信息查询工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化UI组件
        self.create_widgets()
        
        # 默认零件号
        self.part_number_var.set("234-8945")
    
    def create_widgets(self):
        # 零件号输入区域
        input_frame = tk.Frame(self.root, padx=10, pady=10)
        input_frame.pack(fill=tk.X)
        
        tk.Label(input_frame, text="零件号:").pack(side=tk.LEFT)
        self.part_number_var = tk.StringVar()
        part_entry = tk.Entry(input_frame, textvariable=self.part_number_var, width=20)
        part_entry.pack(side=tk.LEFT, padx=5)
        
        query_btn = tk.Button(input_frame, text="查询", command=self.query_part_info)
        query_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tk.Frame(self.root, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(result_frame, text="查询结果:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=20)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮区域
        btn_frame = tk.Frame(self.root, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        save_btn = tk.Button(btn_frame, text="保存结果", command=self.save_results)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame, text="清空结果", command=self.clear_results)
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def query_part_info(self):
        """查询零件信息并显示在界面上"""
        self.clear_results()
        part_number = self.part_number_var.get().strip()
        if not part_number:
            messagebox.showerror("错误", "请输入零件号")
            return
        
        self.result_text.insert(tk.END, f"正在查询零件号: {part_number}\n")
        self.result_text.update()
        
        url = f"https://parts.cat.com/zh-CN/catcorp/{part_number}"
        part_info = self.get_part_info(url)
        
        if part_info:
            self.display_part_info(part_info)
        else:
            self.result_text.insert(tk.END, "查询失败，请检查网络或零件号是否正确\n")
    
    def get_part_info(self, url):
        """获取零件信息（整合之前的功能）"""
        try:
            # 生成随机User-Agent
            ua = UserAgent()
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'Referer': f'https://www.google.com/search?q=Cat+{url.split("/")[-1]}'
            }
            
            time.sleep(random.uniform(2, 5))
            session = requests.Session()
            session.headers = headers
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            if "403 Forbidden" in response.text or "禁止访问" in response.text:
                raise requests.exceptions.RequestException("服务器拒绝访问，可能是反爬机制触发")
            
            # print(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            # print(soup)
            part_info = self.parse_part_info(soup, url.split("/")[-1])
            return part_info
            
        except requests.exceptions.RequestException as e:
            self.result_text.insert(tk.END, f"请求错误: {e}\n")
            if 'response' in locals():
                self.result_text.insert(tk.END, f"响应状态码: {response.status_code}\n")
                self.result_text.insert(tk.END, f"响应内容前200字符: {response.text[:200]}\n")
            return None
        except Exception as e:
            self.result_text.insert(tk.END, f"处理页面时出错: {e}\n")
            return None
    
    def parse_part_info(self, soup, part_number):
        """解析零件信息"""
        part_info = {}
        
        # 提取零件号和名称
        part_name_element = soup.find('h1', class_=re.compile(r'product|main-title'))
        part_name = part_name_element.text.strip() if part_name_element else f"零件号 {part_number}"
        part_info["零件号和名称"] = f"{part_number}: {part_name}"
        
        # 提取品牌
        brand_element = soup.find(string=re.compile(r'品牌:\s*Cat'))
        part_info["品牌"] = brand_element.strip() if brand_element else "未找到品牌信息"
        
        # 提取描述
        description_section = soup.find(string=re.compile(r'描述:'))
        if description_section:
            description = ""
            next_element = description_section.next_sibling
            while next_element and not re.search(r'特性|技术规格|兼容型号', str(next_element)):
                if next_element.strip():
                    description += next_element.strip() + " "
                next_element = next_element.next_sibling
            part_info["描述"] = description.strip()
        
        # 提取特性
        features_section = soup.find(string=re.compile(r'特性:'))
        if features_section:
            features = ""
            next_element = features_section.next_sibling
            while next_element and not re.search(r'技术规格|兼容型号', str(next_element)):
                if next_element.strip():
                    features += next_element.strip() + " "
                next_element = next_element.next_sibling
            part_info["特性"] = features.strip()
        
        # 提取技术规格
        specs_section = soup.find(string=re.compile(r'技术规格'))
        if specs_section:
            specs = {}
            next_element = specs_section.next_sibling
            while next_element and not re.search(r'兼容型号', str(next_element)):
                if next_element.strip():
                    line = next_element.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        specs[key.strip()] = value.strip()
                next_element = next_element.next_sibling
            part_info["技术规格"] = specs
        
        # 提取兼容型号
        compatible_section = soup.find(string=re.compile(r'兼容型号'))
        if compatible_section:
            compatible_models = {}
            next_element = compatible_section.next_sibling
            while next_element and next_element.name not in ['h2', 'h3', 'h4']:
                if next_element.strip():
                    line = next_element.strip()
                    if line and not re.search(r'图表', line):
                        if compatible_section.parent and compatible_section.parent.find_previous('h2'):
                            category = compatible_section.parent.find_previous('h2').text.strip()
                        else:
                            category = "设备类型"
                        if category in compatible_models:
                            compatible_models[category].append(line)
                        else:
                            compatible_models[category] = [line]
                next_element = next_element.next_sibling
            part_info["兼容型号"] = compatible_models
        
        return part_info
    
    def display_part_info(self, part_info):
        """在界面上显示零件信息"""
        for key, value in part_info.items():
            self.result_text.insert(tk.END, f"\n{key}:\n")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    self.result_text.insert(tk.END, f"  {sub_key}: {sub_value}\n")
            elif isinstance(value, list):
                for item in value:
                    self.result_text.insert(tk.END, f"  - {item}\n")
            else:
                self.result_text.insert(tk.END, f"  {value}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.see(tk.END)
    
    def save_results(self):
        """保存查询结果到文件"""
        text = self.result_text.get("1.0", tk.END)
        if "查询失败" in text or "错误" in text:
            messagebox.showinfo("提示", "没有可保存的有效结果")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存查询结果"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("成功", f"结果已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {e}")
    
    def clear_results(self):
        """清空结果显示区域"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "输入零件号并点击查询按钮获取信息...\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CatPartViewer(root)
    root.mainloop()