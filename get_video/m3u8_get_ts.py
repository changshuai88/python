import os
import requests
from urllib.parse import urljoin

# 配置项
M3U8_URL = "https://vip1.lz-cdn.com/20220416/8729_26f95815/1200k/hls/mixed.m3u8"  # 替换为实际的m3u8文件URL
OUTPUT_TXT = "./ts_urls.txt"  # 保存TS地址的文本文件
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def get_response(url, headers=None):
    """发送HTTP请求并返回响应内容"""
    if not headers:
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": urljoin(url, "/")
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"请求错误: {url} - {str(e)}")
        return None

def parse_m3u8(m3u8_content, base_url):
    """解析m3u8文件，提取TS文件URL"""
    ts_urls = []
    lines = m3u8_content.splitlines()
    
    for line in lines:
        line = line.strip()
        # 跳过注释和空行
        if not line or line.startswith("#"):
            continue
        
        # 处理相对路径
        if not line.startswith("http"):
            line = urljoin(base_url, line)
        
        ts_urls.append(line)
    
    return ts_urls

def save_ts_urls(ts_urls, output_file):
    """将TS文件URL保存到文本文件"""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for url in ts_urls:
                f.write(url + "\n")
        print(f"成功保存 {len(ts_urls)} 个TS文件地址到 {output_file}")
        return True
    except Exception as e:
        print(f"保存文件错误: {str(e)}")
        return False

def main():
    print(f"开始解析M3U8文件: {M3U8_URL}")
    
    # 获取m3u8文件内容
    response = get_response(M3U8_URL)
    if not response:
        print("无法获取M3U8文件，程序退出")
        return
    
    # 检查是否有加密信息
    if "#EXT-X-KEY" in response.text:
        print("警告: 检测到加密的TS文件")
    
    # 解析TS文件URL列表
    ts_urls = parse_m3u8(response.text, M3U8_URL)
    print(f"共发现 {len(ts_urls)} 个TS文件地址")
    
    if not ts_urls:
        print("未找到TS文件地址，程序退出")
        return
    
    # 保存TS地址到文本文件
    save_ts_urls(ts_urls, OUTPUT_TXT)

if __name__ == "__main__":
    main()
