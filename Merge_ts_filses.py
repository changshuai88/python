import os


def merge_ts_files(folder_path, output_file):
    # 获取文件夹中所有的TS文件，并按文件名排序
    ts_files = [f for f in os.listdir(folder_path) if f.endswith('.ts')]
    ts_files.sort()

    try:
        # 以二进制追加模式打开输出文件
        with open(output_file, 'ab') as outfile:
            for ts_file in ts_files:
                file_path = os.path.join(folder_path, ts_file)
                try:
                    # 以二进制读取模式打开每个TS文件
                    with open(file_path, 'rb') as infile:
                        # 将当前TS文件的内容写入输出文件
                        outfile.write(infile.read())
                    print(f"已合并 {ts_file}")
                except Exception as e:
                    print(f"合并 {ts_file} 时出错: {e}")
        print(f"所有TS文件已合并到 {output_file}")
    except Exception as e:
        print(f"合并过程中出现错误: {e}")


if __name__ == "__main__":
    # 存放TS文件的文件夹路径，需要根据实际情况修改
    folder_path = 'your_ts_folder'
    # 合并后的输出文件名，需要根据实际情况修改
    output_file = 'merged.ts'
    merge_ts_files(folder_path, output_file)
    