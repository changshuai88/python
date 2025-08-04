from bs4 import BeautifulSoup
import requests

# 使用 requests 获取网页内容
url = 'https://www.shandonghetian.com/sp/361422-1-1.html' # 抓取bing搜索引擎的网页内容
response = requests.get(url)

# 使用 BeautifulSoup 解析网页
soup = BeautifulSoup(response.text, 'lxml')  # 使用 lxml 解析器
# 解析网页内容 html.parser 解析器
# soup = BeautifulSoup(response.text, 'html.parser')
print(soup)
paragraph_text = soup.find('p').get_text()
# print(paragraph_text)

#查找第一个a标签
first_link = soup.find('a')

# print(first_link)
# print('------------')


#获取当前标签的父标签
parent_tag = first_link.parent
# print(parent_tag.get_text())