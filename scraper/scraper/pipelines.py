from asgiref.sync import sync_to_async
from django.db import connections
from django.db.utils import OperationalError
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from apps.translation.models import Article

class ScraperPipeline:
    def process_item(self, item, spider):
        article = Article()
        article.url = item['url']
        article.title = item['title']
        article.author = item['author']
        article.data = item['data']
        article.save()
        return item
