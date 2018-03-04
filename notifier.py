import requests
import bs4
import os
import json
import sys
import datetime
import logging
from exlist import ExList

logger = logging.getLogger(__name__)

class News:
    root = "http://www.baystars.co.jp"
    send_list = []
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    year = str(now.year)
    month = str(now.month) if now.month >= 10 else '0' + str(now.month)
    day = str(now.day) if now.day >=10 else '0' + str(now.day)

    def __str__(self):
        return self.title + "\n(" + News.root + self.path + ")"

    def __init__(self, link):
        self.path = link.get("href")
        self.title = link.string
        [news_year, news_month, news_day] = self.path.split('/')[2:]
        news_day = news_day[2:4]
        if news_year == News.year and news_month == News.month and news_day == News.day:
            News.send_list.append(self)

def main():
    logging.basicConfig()
    logging.getLogger(__name__).setLevel(level=logging.DEBUG)
    try:
        r = requests.get(News.root, timeout=3)
    except requests.exceptions.Timeout:
        logger.debug("Failed to fetch html!!")
        sys.exit(1)
    logger.info("Succeded to fetch html!!")

    soup = bs4.BeautifulSoup(r.text, "html.parser")
    news = ExList(soup.select("ul.newsList")[0].select("li"))

    news.foreach(lambda n: News(n.select("a")[0]))

    if News.send_list:
        message = "\n\n".join(ExList(News.send_list).map(lambda news: news.__str__()))
    else:
        message = "特にお知らせはありません\n"
    logger.info("Message: " + message)

    url = os.getenv("BAYSTARS_URL","")

    try:
        requests.post(url, data = json.dumps({
        'text': message, # 投稿するテキスト
        'username': u'baystars-news', # 投稿のユーザー名
        'link_names': 1, # メンションを有効にする
        }))
    except requests.exceptions.MissingSchema:
        logger.debug("You have not set URL...")
        sys.exit(1)
    logger.info("You have sent message to Slack!")

def exe(event, context):
    main()

if __name__ == '__main__':
    main()

