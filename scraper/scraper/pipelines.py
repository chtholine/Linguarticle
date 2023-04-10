from asgiref.sync import sync_to_async
from django.db import connections
from django.db.utils import OperationalError
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from apps.translation.models import Article


class ScraperPipeline(object):
    def process_item(self, item, spider):
        item.save()
        return item
