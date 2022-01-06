import requests
import bs4
import os
import json
import sys
import datetime
import logging
from concurrent import futures
from exlist import ExList

class News:
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return self.title + "\n(" + self.url + ")"

# return today's date like this
# "/2019/03/0301"
def createTodayDate():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    year = str(now.year)
    month = str(now.month) if now.month >= 10 else '0' + str(now.month)
    day = str(now.day) if now.day >=10 else '0' + str(now.day)
    return '/' + year + '/' + month + '/' + month + day

# return URL like this
# "http://www.baystars.co.jp/news/2019/03/0301_01.php"
def createURL(num):
    root = 'http://www.baystars.co.jp/news'
    suffix = '.php'
    today = createTodayDate()
    index = '0' + str(num+1)
    url = root + today + '_' + index + suffix
    return url

# return News or None
def crawl(num):
    url = createURL(num)
    try:
        r = requests.get(url, timeout=3)
    except requests.exceptions.Timeout:
        return None
    if r.status_code == 404:
        return None
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    title = soup.find('title').text[:-15]
    if title.find("見つかりません") != -1:
        return None
    news = News(title, url)
    return news

def makeText(newslist):
    texts = [news.__str__() for news in newslist if news is not None]
    if len(texts) == 0:
        return "特にお知らせはありません\n"
    return '\n\n'.join(texts)

def sendSlackMessage(message):
    webhookurl = os.getenv("BAYSTARS_URL","")
    try:
        requests.post(webhookurl, data = json.dumps({
        'text': message, # 投稿するテキスト
        'username': u'baystars-news', # 投稿のユーザー名
        'link_names': 1, # メンションを有効にする
        }))
    except requests.exceptions.MissingSchema:
        sys.exit(1)

def main():
    with futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix="thread") as executor:
        newslist = list(executor.map(crawl, range(10)))
    text = makeText(newslist)
    print(text)
    sendSlackMessage(text)

def exe(event, context):
    main()

if __name__ == '__main__':
    main()

