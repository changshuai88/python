
import os
import shutil


def clean_filename(filename):
    # 去除文件名中的 - 符号并转换为小写
    return filename.replace('-', '').lower()


def find_and_copy_unique_images(folder1, folder2, folder3):
    # 确保目标文件夹存在
    if not os.path.exists(folder3):
        os.makedirs(folder3)

    # 获取文件夹 2 中的所有图片名称（去除 - 并转换为小写）
    folder2_image_names = set()
    for root, dirs, files in os.walk(folder2):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                folder2_image_names.add(clean_filename(file))

    # 遍历文件夹 1 中的所有文件
    for root, dirs, files in os.walk(folder1):
        for file in files:
            # 检查文件是否为图片文件（这里简单以常见图片扩展名判断）
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                if clean_filename(file) not in folder2_image_names:
                    # 构建源文件和目标文件的完整路径
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(folder3, file)
                    # 复制文件到目标文件夹
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"Copied {file} to {folder3}")
                    except Exception as e:
                        print(f"Error copying {file}: {e}")


if __name__ == "__main__":
    # 替换为实际的文件夹路径
    folder1 = './renameImage'
    folder2 = r'E:\work\卡特\卡特照片'
    folder3 = r'E:\work\卡特\卡特照片\卡特照片2025'

    find_and_copy_unique_images(folder1, folder2, folder3)
=======
import os
import shutil


def clean_filename(filename):
    # 去除文件名中的 - 符号并转换为小写
    return filename.replace('-', '').lower()


def find_and_copy_unique_images(folder1, folder2, folder3):
    # 确保目标文件夹存在
    if not os.path.exists(folder3):
        os.makedirs(folder3)

    # 获取文件夹 2 中的所有图片名称（去除 - 并转换为小写）
    folder2_image_names = set()
    for root, dirs, files in os.walk(folder2):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                folder2_image_names.add(clean_filename(file))

    # 遍历文件夹 1 中的所有文件
    for root, dirs, files in os.walk(folder1):
        for file in files:
            # 检查文件是否为图片文件（这里简单以常见图片扩展名判断）
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                if clean_filename(file) not in folder2_image_names:
                    # 构建源文件和目标文件的完整路径
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(folder3, file)
                    # 复制文件到目标文件夹
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"Copied {file} to {folder3}")
                    except Exception as e:
                        print(f"Error copying {file}: {e}")


if __name__ == "__main__":
    # 替换为实际的文件夹路径
    folder1 = './renameImage'
    folder2 = r'E:\work\卡特\卡特照片'
    folder3 = r'E:\work\卡特\卡特照片\卡特照片2025'

    find_and_copy_unique_images(folder1, folder2, folder3)
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
    