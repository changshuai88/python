import requests
from bs4 import BeautifulSoup
import datetime
import time
import random
from fake_useragent import UserAgent

# 模拟真实浏览器的请求头（更完整的字段）
def get_headers():
    ua = UserAgent()
    return {
        "User-Agent": ua.chrome,  # 使用Chrome浏览器的User-Agent，更稳定
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",  # 模拟从谷歌搜索进入，增加真实性
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }

# 解析相对时间（如"3小时前"、"5分钟前"）
def parse_relative_time(time_str):
    now = datetime.datetime.now()
    time_str = time_str.lower().strip()
    
    if "hour" in time_str:
        hours = int(time_str.split()[0])
        return now - datetime.timedelta(hours=hours)
    elif "minute" in time_str:
        mins = int(time_str.split()[0])
        return now - datetime.timedelta(minutes=mins)
    elif "day" in time_str:
        days = int(time_str.split()[0])
        return now - datetime.timedelta(days=days)
    elif "just now" in time_str or "moments ago" in time_str:
        return now
    else:
        return datetime.datetime(1970, 1, 1)  # 无法解析的时间视为非今天

def fetch_reuters_news(session):
    """使用会话保持机制获取路透社新闻"""
    url = "https://www.reuters.com/business/energy/"
    try:
        # 增加延迟（3-5秒），降低反爬概率
        time.sleep(random.uniform(3, 5))
        response = session.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()  # 检查HTTP状态码
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 路透社页面结构可能更新，调整选择器（通过浏览器F12确认）
        news_items = soup.find_all("div", class_="story-card")  # 新的类名，原"story-content"可能已失效
        today = datetime.date.today()
        results = []
        
        for item in news_items:
            try:
                title_tag = item.find("h3", class_="story-card__title")
                if not title_tag:
                    continue
                title = title_tag.text.strip()
                
                link_tag = title_tag.find_parent("a")
                if not link_tag:
                    continue
                link = link_tag["href"]
                if link.startswith("/"):
                    link = f"https://www.reuters.com{link}"
                
                # 解析发布时间
                time_tag = item.find("time", class_="story-card__timestamp")
                if not time_tag:
                    continue
                time_str = time_tag["datetime"]
                pub_date = datetime.datetime.fromisoformat(time_str).date()
                
                if pub_date == today:
                    results.append({
                        "source": "Reuters",
                        "title": title,
                        "link": link,
                        "published": time_str.split("T")[1].split(".")[0]
                    })
            except Exception as e:
                print(f"路透社单条解析失败: {str(e)}")
                continue
                
        return results
    
    except Exception as e:
        print(f"路透社抓取失败: {str(e)}")
        return []

def fetch_investing_news(session):
    url = "https://www.investing.com/news/commodities-news/"
    try:
        time.sleep(random.uniform(3, 5))
        response = session.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        news_items = soup.find_all("article", class_="articleItem")
        today = datetime.date.today()
        results = []
        
        for item in news_items:
            try:
                title_tag = item.find("a", class_="title")
                if not title_tag:
                    continue
                title = title_tag.text.strip()
                link = title_tag["href"]
                if link.startswith("/"):
                    link = f"https://www.investing.com{link}"
                
                time_tag = item.find("time") or item.find("div", class_="date")
                if not time_tag:
                    continue
                time_str = time_tag.text.strip()
                
                pub_datetime = parse_relative_time(time_str)
                if pub_datetime.date() == today:
                    results.append({
                        "source": "Investing.com",
                        "title": title,
                        "link": link,
                        "published": time_str
                    })
            except Exception as e:
                print(f"Investing单条解析失败: {str(e)}")
                continue
                
        return results
    
    except Exception as e:
        print(f"Investing.com抓取失败: {str(e)}")
        return []

def main():
    print("开始抓取今日石油相关资讯...\n")
    
    # 创建会话对象（自动处理cookies，模拟真实用户会话）
    session = requests.Session()
    
    # 先访问一个无关页面获取初始cookies（增加真实性）
    try:
        session.get("https://www.google.com", headers=get_headers(), timeout=10)
        time.sleep(2)
    except:
        pass
    
    # 抓取新闻
    reuters_news = fetch_reuters_news(session)
    investing_news = fetch_investing_news(session)
    
    # 合并去重
    all_news = reuters_news + investing_news
    seen_titles = set()
    unique_news = []
    for news in all_news:
        if news["title"] not in seen_titles:
            seen_titles.add(news["title"])
            unique_news.append(news)
    
    # 按时间排序
    unique_news.sort(key=lambda x: x["published"], reverse=True)
    
    # 输出结果
    print(f"今日石油资讯汇总 ({len(unique_news)}条):")
    for idx, news in enumerate(unique_news, 1):
        print(f"\n{idx}. [{news['source']}]")
        print(f"   标题: {news['title']}")
        print(f"   链接: {news['link']}")
        print(f"   发布时间: {news['published']}")

if __name__ == "__main__":
    main()