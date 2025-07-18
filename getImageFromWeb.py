import requests
from bs4 import BeautifulSoup
import os

def get_image_links(url):
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    """
    从指定 URL 中提取所有图片的链接
    :param url: 目标网站的 URL
    :return: 图片链接列表
    """
    try:
        # 发送 HTTP 请求获取网页内容
        # response = requests.get(url)
        # 使用请求头发送青丘并获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # 使用 BeautifulSoup 解析 HTML 页面
        soup = BeautifulSoup(response.text, 'html.parser')
        image_links = []
        # 查找所有的 img 标签
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('http'):
                image_links.append(src)
            else:
                # 处理相对链接
                base_url = url.rsplit('/', 1)[0]
                image_links.append(f"{base_url}/{src}")
        return image_links
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return []

def download_image(url, save_path):
    # 下载也需要设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    """
    下载指定 URL 的图片到本地
    :param url: 图片的 URL
    :param save_path: 保存图片的本地路径
    """
    try:
        # 发送 HTTP 请求获取图片内容
        # response = requests.get(url, stream=True)
        # 发送 HTTP 请求,添加请求头，获取图片内容
        response = requests.get(url, headers=headers, stream=True)

        response.raise_for_status()
        # 以二进制写入模式打开文件
        with open(save_path, 'wb') as file:
            # 分块写入文件，避免一次性加载大量数据
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"下载成功: {save_path}")
    except requests.RequestException as e:
        print(f"下载出错: {e}")

def main(url, save_dir):
    """
    主函数，用于爬取网站上的图片并下载到本地
    :param url: 目标网站的 URL
    :param save_dir: 保存图片的本地目录
    """
    # 如果保存目录不存在，则创建该目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 获取图片链接列表
    image_links = get_image_links(url)
    for i, image_link in enumerate(image_links, start=1):
        # 生成保存图片的文件名
        file_extension = os.path.splitext(image_link.split('/')[-1])[1]
        file_name = os.path.join(save_dir, f"image_{i}{file_extension}")
        # 下载图片
        download_image(image_link, file_name)

if __name__ == "__main__":
    # 替换为你要爬取的网站 URL
    target_url = "https://parts.cat.com/zh-CN/catcorp/112-5060"
    # 保存图片的本地目录
    save_directory = "./getImageFromWeb"
    main(target_url, save_directory)