import os
import asyncio
import aiohttp
import argparse
from typing import List

# 配置项
DEFAULT_TS_FILE = "ts_urls.txt"  # 默认的TS地址文件
DEFAULT_SAVE_DIR = "downloaded_ts"  # 默认保存目录
MAX_CONCURRENT = 5  # 最大并发数
TIMEOUT = 30  # 超时时间(秒)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

def read_ts_urls(file_path: str) -> List[str]:
    """从文本文件读取TS地址列表"""
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 读取所有非空行，忽略注释行
            urls = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        
        print(f"从 {file_path} 成功读取 {len(urls)} 个TS地址")
        return urls
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        return []

async def download_single_ts(
    session: aiohttp.ClientSession, 
    url: str, 
    index: int, 
    save_dir: str, 
    semaphore: asyncio.Semaphore
) -> None:
    """异步下载单个TS文件"""
    # 生成有序的文件名
    filename = os.path.join(save_dir, f"segment_{index:04d}.ts")
    
    # 检查文件是否已存在
    if os.path.exists(filename):
        print(f"[{index+1}] 已存在，跳过: {os.path.basename(filename)}")
        return
    
    async with semaphore:
        try:
            # 发送请求
            async with session.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Referer": "https://www.example.com/"
                },
                timeout=TIMEOUT
            ) as response:
                response.raise_for_status()
                
                # 读取并保存内容
                content = await response.read()
                with open(filename, "wb") as f:
                    f.write(content)
                
                print(f"[{index+1}] 下载完成: {os.path.basename(filename)}")
                
        except aiohttp.ClientResponseError as e:
            print(f"[{index+1}] HTTP错误 {e.status}: {url}")
        except aiohttp.ClientError as e:
            print(f"[{index+1}] 网络错误: {url} - {str(e)}")
        except asyncio.TimeoutError:
            print(f"[{index+1}] 超时: {url}")
        except Exception as e:
            print(f"[{index+1}] 下载失败: {url} - {str(e)}")

async def main(file_path: str, save_dir: str):
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    print(f"TS文件将保存到: {os.path.abspath(save_dir)}")
    
    # 读取TS地址列表
    ts_urls = read_ts_urls(file_path)
    if not ts_urls:
        print("没有有效的TS地址可下载，程序退出")
        return
    
    # 创建异步会话
    async with aiohttp.ClientSession() as session:
        # 限制并发数
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # 创建所有下载任务
        tasks = [
            download_single_ts(session, url, index, save_dir, semaphore)
            for index, url in enumerate(ts_urls)
        ]
        
        # 执行所有任务
        await asyncio.gather(*tasks)
        
        print("\n所有下载任务已处理完毕")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="从txt文件读取TS地址并异步下载")
    parser.add_argument("-f", "--file", default=DEFAULT_TS_FILE, 
                      help=f"包含TS地址的文本文件，默认: {DEFAULT_TS_FILE}")
    parser.add_argument("-d", "--dir", default=DEFAULT_SAVE_DIR, 
                      help=f"TS文件保存目录，默认: {DEFAULT_SAVE_DIR}")
    
    args = parser.parse_args()
    
    # 处理Windows系统事件循环问题
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 运行主程序
    asyncio.run(main(args.file, args.dir))
