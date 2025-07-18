import httpx
import asyncio
import os
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从 txt 文件中读取 URL 列表
def read_urls_from_file(file_path):
    url_list = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                url = line.strip()
                if url:
                    url_list.append(url)
        return url_list
    except FileNotFoundError:
        logging.error("未找到指定的 txt 文件，请检查文件路径和文件名。")
        return []

# 确保 film 文件夹存在
if not os.path.exists('film'):
    os.makedirs('film')

async def download_image(client, url, semaphore):
    async with semaphore:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                # 从 URL 中提取文件名
                filename = os.path.join('film', url.split("/")[-1])
                # 以二进制写入模式打开文件
                with open(filename, 'wb') as f:
                    # 读取响应内容并写入文件
                    f.write(response.content)
                logging.info(f"下载成功: {filename}")
            else:
                logging.error(f"下载失败: {url}, 状态码: {response.status_code}")
        except Exception as e:
            logging.error(f"下载失败: {url}, 错误信息: {e}")

async def main(urls, max_concurrency=10):
    semaphore = asyncio.Semaphore(max_concurrency)
    async with httpx.AsyncClient() as client:
        # 创建任务列表
        tasks = [download_image(client, url, semaphore) for url in urls]
        # 并发执行所有任务
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    file_path = './film/111.txt'
    url_list = read_urls_from_file(file_path)
    if url_list:
        asyncio.run(main(url_list))