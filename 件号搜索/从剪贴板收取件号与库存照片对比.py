import os
import pyperclip
import re

def get_clipboard_data():
    """
    读取剪贴板中的数据，去除横线并去重，返回处理后的关键词列表
    """
    # 读取剪贴板文本
    clipboard_text = pyperclip.paste()
    if not clipboard_text:
        print("⚠️ 剪贴板为空，请先复制需要对比的内容！")
        return []
    
    # 按换行分割，去除空行和首尾空格
    raw_keywords = [line.strip() for line in clipboard_text.split('\n') if line.strip()]
    # 核心优化：去除每个关键词中的横线 -
    processed_keywords = [keyword.replace('-', '') for keyword in raw_keywords]
    # 去重（避免重复对比）
    unique_keywords = list(set(processed_keywords))
    
    # 打印处理前后的对比，方便核对
    print(f"\n📋 剪贴板原始数据：{raw_keywords}")
    print(f"✅ 处理后（去横线+去重）：{unique_keywords}")
    return unique_keywords

def find_duplicate_images(folder_path, keywords):
    """
    遍历文件夹及子文件夹，去除图片文件名中的横线后，查找匹配的图片
    :param folder_path: 目标文件夹路径
    :param keywords: 处理后的待对比关键词列表
    """
    # 定义需要匹配的图片后缀（可根据需要添加）
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.psd', '.webp', '.bmp')
    duplicate_results = []  # 存储重复结果
    
    # 遍历文件夹（包括子文件夹）
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 筛选图片文件
            if file.lower().endswith(image_extensions):
                # 分离文件名和后缀（避免后缀干扰匹配）
                file_name_without_ext = os.path.splitext(file)[0]
                # 核心优化：去除文件名中的横线 -
                processed_file_name = file_name_without_ext.replace('-', '')
                
                # 遍历每个关键词，检查是否匹配
                for keyword in keywords:
                    if keyword in processed_file_name:
                        file_path = os.path.join(root, file)
                        duplicate_results.append({
                            '匹配关键词（去横线）': keyword,
                            '原始图片文件名': file,
                            '处理后图片名（去横线）': processed_file_name,
                            '图片完整路径': file_path
                        })
    
    # 输出结果
    if duplicate_results:
        print("\n🔍 找到以下重复匹配项：")
        for idx, result in enumerate(duplicate_results, 1):
            print(f"\n{idx}. 匹配关键词：{result['匹配关键词（去横线）']}")
            print(f"   原始图片名：{result['原始图片文件名']}")
            print(f"   处理后图片名：{result['处理后图片名（去横线）']}")
            print(f"   图片路径：{result['图片完整路径']}")
    else:
        print("\n✅ 未找到任何匹配的图片文件名！")

if __name__ == "__main__":
    # -------------------------- 配置区（请修改这里）--------------------------
    # 替换为你要检查的文件夹路径（Windows路径用双反斜杠 \\ 或单斜杠 /）
    TARGET_FOLDER = r"E:\work\卡特\卡特照片"
    # -------------------------------------------------------------------------
    
    # 步骤1：读取并处理剪贴板关键词
    check_keywords = get_clipboard_data()
    if not check_keywords:
        exit()  # 剪贴板为空则退出
    
    # 步骤2：检查文件夹是否存在
    if not os.path.exists(TARGET_FOLDER):
        print(f"⚠️ 错误：文件夹路径 {TARGET_FOLDER} 不存在！")
        exit()
    
    # 步骤3：查找重复图片
    find_duplicate_images(TARGET_FOLDER, check_keywords)