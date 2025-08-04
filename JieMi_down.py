
import httpx
import asyncio
import os
import logging
from Crypto.Cipher import AES 


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


async def download_file(client, url, save_path):
    try:
        response = await client.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    except httpx.RequestError as e:
        logging.error(f"下载文件时出错: {url}, 错误信息: {e}")
        return False


def decrypt_ts_file(encrypted_file_path, decrypted_file_path, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)


async def download_and_decrypt_ts(client, ts_url, key_url, iv_hex, save_dir, semaphore):
    async with semaphore:
        # 下载加密密钥
        key_file_path = os.path.join(save_dir, 'enc.key')
        if not await download_file(client, key_url, key_file_path):
            return
        with open(key_file_path, 'rb') as key_file:
            key = key_file.read()

        # 解析初始向量
        iv = bytes.fromhex(iv_hex[2:])

        # 下载TS文件
        ts_file_name = ts_url.split('/')[-1]
        encrypted_ts_path = os.path.join(save_dir, ts_file_name)
        if not await download_file(client, ts_url, encrypted_ts_path):
            return

        # 解密TS文件
        decrypted_ts_path = os.path.join(save_dir, f'decrypted_{ts_file_name}')
        decrypt_ts_file(encrypted_ts_path, decrypted_ts_path, key, iv)

        logging.info(f"TS文件已下载并解密到 {decrypted_ts_path}")


async def main(urls, ts_urls, key_url, iv_hex, max_concurrency=10):
    semaphore = asyncio.Semaphore(max_concurrency)
    async with httpx.AsyncClient() as client:
        # 创建图片下载任务列表
        image_tasks = [download_image(client, url, semaphore) for url in urls]
        # 创建TS文件下载解密任务列表
        ts_tasks = [download_and_decrypt_ts(client, ts_url, key_url, iv_hex, 'film', semaphore) for ts_url in ts_urls]
        # 并发执行所有任务
        await asyncio.gather(*image_tasks, *ts_tasks)


if __name__ == "__main__":
    file_path = './film/111.txt'
    url_list = read_urls_from_file(file_path)
    # 替换为实际的TS文件URL列表
    ts_urls = ["https://example.com/path/to/your1.ts", "https://example.com/path/to/your2.ts"]
    # 替换为实际的密钥文件URL
    key_url = "https://hd.ijycnd.com/play/1aMoPGAd/enc.key"
    # 初始向量
    iv_hex = "0x00000000000000000000000000000000"
    if url_list or ts_urls:
        asyncio.run(main(url_list, ts_urls, key_url, iv_hex))
=======
import httpx
import asyncio
import os
import logging
from Crypto.Cipher import AES 


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


async def download_file(client, url, save_path):
    try:
        response = await client.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return True
    except httpx.RequestError as e:
        logging.error(f"下载文件时出错: {url}, 错误信息: {e}")
        return False


def decrypt_ts_file(encrypted_file_path, decrypted_file_path, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)


async def download_and_decrypt_ts(client, ts_url, key_url, iv_hex, save_dir, semaphore):
    async with semaphore:
        # 下载加密密钥
        key_file_path = os.path.join(save_dir, 'enc.key')
        if not await download_file(client, key_url, key_file_path):
            return
        with open(key_file_path, 'rb') as key_file:
            key = key_file.read()

        # 解析初始向量
        iv = bytes.fromhex(iv_hex[2:])

        # 下载TS文件
        ts_file_name = ts_url.split('/')[-1]
        encrypted_ts_path = os.path.join(save_dir, ts_file_name)
        if not await download_file(client, ts_url, encrypted_ts_path):
            return

        # 解密TS文件
        decrypted_ts_path = os.path.join(save_dir, f'decrypted_{ts_file_name}')
        decrypt_ts_file(encrypted_ts_path, decrypted_ts_path, key, iv)

        logging.info(f"TS文件已下载并解密到 {decrypted_ts_path}")


async def main(urls, ts_urls, key_url, iv_hex, max_concurrency=10):
    semaphore = asyncio.Semaphore(max_concurrency)
    async with httpx.AsyncClient() as client:
        # 创建图片下载任务列表
        image_tasks = [download_image(client, url, semaphore) for url in urls]
        # 创建TS文件下载解密任务列表
        ts_tasks = [download_and_decrypt_ts(client, ts_url, key_url, iv_hex, 'film', semaphore) for ts_url in ts_urls]
        # 并发执行所有任务
        await asyncio.gather(*image_tasks, *ts_tasks)


if __name__ == "__main__":
    file_path = './film/111.txt'
    url_list = read_urls_from_file(file_path)
    # 替换为实际的TS文件URL列表
    ts_urls = ["https://example.com/path/to/your1.ts", "https://example.com/path/to/your2.ts"]
    # 替换为实际的密钥文件URL
    key_url = "https://hd.ijycnd.com/play/1aMoPGAd/enc.key"
    # 初始向量
    iv_hex = "0x00000000000000000000000000000000"
    if url_list or ts_urls:
        asyncio.run(main(url_list, ts_urls, key_url, iv_hex))
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
    