import os
import shutil  # 新增：用于跨磁盘复制文件
import subprocess
import argparse
import tempfile
from typing import List

# 配置项 - 默认为每次合并50个文件
DEFAULT_TS_DIR = "downloaded_ts"  # 默认TS文件目录
DEFAULT_OUTPUT_FILE = "merged.ts"  # 合并后的TS文件名
BATCH_SIZE = 50  # 每批合并的文件数量

def get_sorted_ts_files(ts_dir: str) -> List[str]:
    """获取目录中按文件名排序的TS文件列表"""
    if not os.path.isdir(ts_dir):
        print(f"错误：目录 '{ts_dir}' 不存在或不是一个有效目录")
        return []
    
    # 筛选出所有TS文件
    ts_files = [
        f for f in os.listdir(ts_dir) 
        if f.lower().endswith(".ts") and os.path.isfile(os.path.join(ts_dir, f))
    ]
    
    if not ts_files:
        print(f"警告：在目录 '{ts_dir}' 中未找到任何TS文件")
        return []
    
    # 按文件名排序（确保分片顺序正确）
    ts_files.sort()
    
    # 生成完整路径列表
    sorted_ts_paths = [os.path.join(ts_dir, f) for f in ts_files]
    
    # 显示找到的文件信息
    print(f"找到 {len(sorted_ts_paths)} 个TS文件，将按每批{BATCH_SIZE}个顺序合并")
    return sorted_ts_paths

def merge_in_batches(ts_files: List[str], output_file: str) -> bool:
    """分批合并TS文件，解决跨磁盘移动问题"""
    if not ts_files:
        print("错误：没有可合并的TS文件")
        return False
    
    # 如果文件数量少于等于批次大小，直接合并
    if len(ts_files) <= BATCH_SIZE:
        return merge_single_batch(ts_files, output_file)
    
    # 创建临时目录存储中间结果
    with tempfile.TemporaryDirectory(prefix="ts_merge_") as temp_dir:
        print(f"使用临时目录处理分批合并：{temp_dir}")
        
        # 第一批合并BATCH_SIZE个文件
        current_batch = ts_files[:BATCH_SIZE]
        remaining_files = ts_files[BATCH_SIZE:]
        current_output = os.path.join(temp_dir, "batch_0.ts")
        
        if not merge_single_batch(current_batch, current_output):
            return False
        
        # 后续批次合并
        batch_num = 1
        while remaining_files:
            take_count = min(BATCH_SIZE - 1, len(remaining_files))
            batch_files = [current_output] + remaining_files[:take_count]
            remaining_files = remaining_files[take_count:]
            
            next_output = os.path.join(temp_dir, f"batch_{batch_num}.ts")
            
            print(f"正在合并第 {batch_num+1} 批文件（共{BATCH_SIZE}个），剩余 {len(remaining_files)} 个文件...")
            if not merge_single_batch(batch_files, next_output):
                return False
            
            current_output = next_output
            batch_num += 1
        
        # 修复跨磁盘移动问题：先检查是否同磁盘，不同则复制
        try:
            # 检查源文件和目标文件是否在同一磁盘
            if os.path.splitdrive(current_output)[0] == os.path.splitdrive(output_file)[0]:
                # 同一磁盘，使用rename高效移动
                if os.path.exists(output_file):
                    os.remove(output_file)
                os.rename(current_output, output_file)
            else:
                # 不同磁盘，使用复制+删除
                if os.path.exists(output_file):
                    os.remove(output_file)
                shutil.copy2(current_output, output_file)  # 复制文件（保留元数据）
                os.remove(current_output)  # 删除临时文件
                
            print(f"\n成功合并为文件：{os.path.abspath(output_file)}")
            print(f"文件大小：{os.path.getsize(output_file) / (1024*1024):.2f} MB")
            return True
            
        except Exception as e:
            print(f"移动最终文件失败：{str(e)}")
            return False

def merge_single_batch(ts_files: List[str], output_file: str) -> bool:
    """合并单个批次的TS文件"""
    try:
        if os.name == "nt":  # Windows系统
            cmd = f'copy /b {"+".join(ts_files)} "{output_file}"'
        else:  # Linux/Mac系统
            cmd = f'cat {" ".join(ts_files)} > "{output_file}"'
        
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        else:
            print("错误：合并后的文件不存在或为空")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"合并命令执行失败：{e.stderr}")
        return False
    except Exception as e:
        print(f"合并过程发生错误：{str(e)}")
        return False

def main():
    global BATCH_SIZE
    
    parser = argparse.ArgumentParser(description=f"分批合并TS文件（默认每批{BATCH_SIZE}个）")
    parser.add_argument("-d", "--dir", default=DEFAULT_TS_DIR,
                      help=f"TS文件所在目录（默认：{DEFAULT_TS_DIR}）")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_FILE,
                      help=f"合并后的TS文件名（默认：{DEFAULT_OUTPUT_FILE}）")
    parser.add_argument("-b", "--batch", type=int, default=BATCH_SIZE,
                      help=f"每批合并的文件数量（默认：{BATCH_SIZE}）")
    
    args = parser.parse_args()
    
    BATCH_SIZE = args.batch
    if BATCH_SIZE != 50:
        print(f"注意：已将每批合并数量调整为 {BATCH_SIZE}")
    
    ts_files = get_sorted_ts_files(args.dir)
    if not ts_files:
        return
    
    merge_in_batches(ts_files, args.output)

if __name__ == "__main__":
    main()
