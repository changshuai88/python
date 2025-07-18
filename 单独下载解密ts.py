import requests
from Crypto.Cipher import AES
import os
import logging


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"下载文件时出错: {e}")
        return False


def decrypt_ts_file(encrypted_file_path, decrypted_file_path, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)


def download_and_decrypt_ts(ts_url, key_url, iv_hex, save_dir):
    # 下载加密密钥
    key_file_path = os.path.join(save_dir, 'enc.key')
    if not download_file(key_url, key_file_path):
        return
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()

    # 解析初始向量
    iv = bytes.fromhex(iv_hex[2:])

    # 下载 TS 文件
    ts_file_name = ts_url.split('/')[-1]
    encrypted_ts_path = os.path.join(save_dir, ts_file_name)
    if not download_file(ts_url, encrypted_ts_path):
        return

    # 解密 TS 文件
    decrypted_ts_path = os.path.join(save_dir, f'decrypted_{ts_file_name}')
    decrypt_ts_file(encrypted_ts_path, decrypted_ts_path, key, iv)

    print(f"TS 文件已下载并解密到 {decrypted_ts_path}")
# 读取文件中的url
# 返回一个列表url_list
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


if __name__ == "__main__":
    # 替换为实际的 TS 文件 URL
    ts_url = "https://c.baisiweiting.com:18443/hls/210/20240116/1075864/plist0.ts"
    # 替换为实际的密钥文件 URL
    key_url = "https://hd.ijycnd.com/play/1aMoPGAd/enc.key"
    # 初始向量
    iv_hex = "0x00000000000000000000000000000000"
    # 保存文件的目录
    save_dir = "./film"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    download_and_decrypt_ts(ts_url, key_url, iv_hex, save_dir)
    