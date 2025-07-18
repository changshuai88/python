# import requests
# import os
# from bs4 import BeautifulSoup

#     # file.write(current_date + '战国策\n')
# def get_span_tags():
#     url = 'https://www.gushiwen.cn/guwen/book_f78a4fd3134a.aspx'
#     headers = {
#         'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
#     }
#     try:
#         # 发送请求获取网页内容
#         response = requests.get(url = url,headers=headers).text
#         # print(response)
#         # response.raise_for_status()

#         # 使用BeautifulSoup解析HTML
#         soup = BeautifulSoup(response, 'html.parser')

#         # 查找所有width为355的span标签
#         # span_tags = soup.find_all('a', href=lambda value: value and '/guwen/bookv*' in value)
#         span_tags = soup.find_all('a', href=lambda value: value and value.startswith('/guwen/bookv'))
#         # print(span_tags)

#         # 打印结果
#         # url_main = 'https://www.gushiwen.cn/'
#         for tag in span_tags:
#             if tag:
#              href = tag.get('href')
#             #  print (href)
#             if href:
#                 prefix = 'https://www.gushiwen.cn'
#                 tag['href'] = prefix + href
#                 response_ziyemian = requests.get(url = tag['href'],headers=headers).text
#                 soup = BeautifulSoup(response_ziyemian, 'html.parser')
#                 div_tags_with_class = soup.find_all('div', class_='contson')[0]
#                 print(div_tags_with_class.text)
#                 with open('./战国策.txt', 'a',encoding='utf-8') as file:
#                     file.write(tag.text + '\n' + div_tags_with_class.text + '\n' +"--------------------------------------------------"+'\n')

#             else:print("下载完成！")

#     except requests.RequestException as e:
#         print(f"请求发生错误: {e}")
#     except Exception as e:
#         print(f"发生错误: {e}")


# if __name__ == "__main__":
#     get_span_tags()


import requests
import os
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

# 定义重试机制，最多重试3次，每次重试间隔2秒
@retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
def make_request(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def get_span_tags():
    url = 'https://www.gushiwen.cn/guwen/book_062f613e0366.aspx'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    }
    try:
        # 发送请求获取网页内容
        response = make_request(url, headers)

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response, 'html.parser')

        # 查找所有href以/guwen/bookv开头的a标签
        span_tags = soup.find_all('a', href=lambda value: value and value.startswith('/guwen/bookv'))
        num = len(span_tags)
        # 打印结果
        prefix = 'https://www.gushiwen.cn'
        for tag in span_tags:
            # num = len(span_tags)
            # print(num)
            href = tag.get('href')
            if href:
                tag['href'] = prefix + href
                # 控制请求频率，每次请求间隔1秒
                import time
                time.sleep(1)
                response_ziyemian = make_request(tag['href'], headers)
                soup = BeautifulSoup(response_ziyemian, 'html.parser')
                div_tags_with_class = soup.find_all('div', class_='contson')[0]
                num -=1
                print(f"剩余待写入数量: {num}")
                with open('./水浒传.txt', 'a', encoding='utf-8') as file:
                    file.write(tag.text + '\n' + div_tags_with_class.text + '\n' + "--------------------------------------------------" + '\n')

        print("下载完成！")

    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    get_span_tags()
    