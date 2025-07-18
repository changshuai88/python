import os


def delete_images(folder_path, txt_file_path):
    try:
        # 读取 txt 文件中的图片名字
        with open(txt_file_path, 'r') as file:
            image_names = [line.strip() for line in file.readlines()]

        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            if filename in image_names:
                file_path = os.path.join(folder_path, filename)
                # 删除文件
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
    except FileNotFoundError:
        print("错误: 文件或文件夹未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")


if __name__ == "__main__":
    folder_path = r'E:\work\卡特\卡特 - 抖音'  # 请替换为实际的图片文件夹路径
    txt_file_path = './keyWord.txt'  # 请替换为实际的 txt 文件路径
    delete_images(folder_path, txt_file_path)
print("执行完毕")