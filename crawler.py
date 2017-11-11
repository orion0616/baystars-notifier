import requests
import bs4
import os

class News:
    root = "http://www.baystars.co.jp/"
    file_name = "past-news.txt"
    past_news = set()
    send_list = []

    @staticmethod
    def load_news():
        with open(News.file_name, 'r') as fin:
            lines = list(map(lambda news: news.strip(),fin.readlines()))
            News.past_news = set(lines)

    @staticmethod
    def save_news():
        with open(News.file_name, 'w') as fout:
            news = list(map(lambda news: news + "\n",list(News.past_news)))
            fout.writelines(news)

    def __str__(self):
        return self.title + "\n(" + News.root + self.path + ")"

    def __init__(self, link):
        self.path = link.get("href")
        self.title = link.string
        if not self.path in News.past_news:
            News.past_news.add(self.path)
            News.send_list.append(self)

News.load_news()
r = requests.get(News.root)
soup = bs4.BeautifulSoup(r.text, "html.parser")
elems = soup.select("ul.newsList")[0].select("li")

for elem in elems:
    link = elem.select("a")[0]
    news = News(link)

if News.send_list:
    message = "\n\n".join(list(map(lambda news: news.__str__(),News.send_list)))
else:
    message = "特にお知らせはありません\n"
print(message)
