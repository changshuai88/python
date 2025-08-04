import os
import shutil

def get_image_filenames(folder_path):
    """获取指定文件夹中所有图片的文件名（不含路径）"""
    # 定义常见图片文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    
    # 存储文件名的集合（集合查找效率更高）
    image_files = set()
    
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"警告：文件夹 {folder_path} 不存在")
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

def copy_missing_images(source_dir, match_dir, dest_dir):
    """复制源文件夹中在匹配文件夹不存在的图片到目标文件夹"""
    # 获取匹配文件夹中的图片文件名集合
    match_images = get_image_filenames(match_dir)
    print(f"在匹配文件夹 {match_dir} 中找到 {len(match_images)} 张图片")
    
    # 确保目标文件夹存在
    os.makedirs(dest_dir, exist_ok=True)
    print(f"目标文件夹：{dest_dir}（若不存在已自动创建）")
    
    # 定义图片文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    
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
                    print(f"已复制：{filename}")
                    copied_files += 1
                except Exception as e:
                    print(f"复制失败 {filename}：{str(e)}")
    
    # 输出统计结果
    print(f"\n处理完成：共检查 {total_files} 张图片，复制了 {copied_files} 张缺失图片")

if __name__ == "__main__":
    # 定义文件夹路径（使用原始字符串避免转义问题）
    source_directory = r"F:\python\renameImage"          # 源图片文件夹
    match_directory = r"E:\work\卡特\卡特照片"            # 用于匹配的图片文件夹
    destination_directory = r"E:\work\卡特\卡特照片\卡特照片2025"  # 复制目标文件夹
    
    # 执行复制操作
    copy_missing_images(source_directory, match_directory, destination_directory)