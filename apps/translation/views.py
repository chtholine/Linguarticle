from rest_framework.views import APIView
from rest_framework.response import Response
from scrapy.crawler import CrawlerProcess
from .myspider import ArticleSpider


class ScrapingView(APIView):
    def get(self, request):
        process = CrawlerProcess(settings={
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'FEED_FORMAT': 'json',
            'FEED_URI': 'output.json',
        })

        process.crawl(ArticleSpider)
        process.start()

        with open('output.json', 'r') as f:
            data = f.read()

        return Response(data)
