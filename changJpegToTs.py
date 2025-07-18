import os

def rename_jpeg_to_ts(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"指定的文件夹 {folder_path} 不存在。")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为 JPEG 格式
        if filename.lower().endswith(('.jpeg', '.jpg')):
            # 构建新的文件名，将扩展名改为 .ts
            new_filename = os.path.splitext(filename)[0] + '.ts'
            # 构建原文件和新文件的完整路径
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            try:
                # 重命名文件
                os.rename(old_file_path, new_file_path)
                print(f"已将 {old_file_path} 重命名为 {new_file_path}")
            except Exception as e:
                print(f"重命名 {old_file_path} 时出错: {e}")

if __name__ == "__main__":
    # 替换为实际的文件夹路径
    folder_path = './film'
    rename_jpeg_to_ts(folder_path)