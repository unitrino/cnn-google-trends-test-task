import asyncio
import random
import feedparser
from aiohttp import web
from bs4 import BeautifulSoup
import nltk


def get_cnn_rss_news(url):
    titles = [k for k in feedparser.parse(url).items()][1][1]
    return map(lambda x: x['title'], titles)


def get_google_trends(url):
    titles = [k for k in feedparser.parse(url).items()][1][1]
    return [i.text.split()
            for i in BeautifulSoup(titles[0]['content'][0]['value'],
                                   'html.parser').find_all('a')]


async def handle(request):
    await asyncio.sleep(random.randint(1, 10))
    loop = asyncio.get_event_loop()

    cnn_news = await loop.run_in_executor(None, get_cnn_rss_news,
                                   'http://rss.cnn.com/rss/edition.rss')
    google_trends = await loop.run_in_executor(None, get_google_trends,
                                   'https://trends.google.com/trends/hottrends/atom/hourly')

    google_trends = {j.lower() for i in google_trends for j in i}
    cnn_news = [i.lower() for i in cnn_news]

    google_trends = {i for i in google_trends
                     if nltk.pos_tag(nltk.word_tokenize(i))[0][1] == 'NN'
                     or
                     nltk.pos_tag(nltk.word_tokenize(i))[0][1] == 'NNS'}

    answ = [j for i in google_trends for j in cnn_news if i in j]
    return web.Response(text=str(set(answ)))



app = web.Application()
app.add_routes([web.get('/', handle)])

web.run_app(app)