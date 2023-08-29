import re
from typing import NamedTuple
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import scrapy
from ..items import ArticleItem


class ArticleSpider(scrapy.Spider):
    name = "article_spider"

    def __init__(self, user_id=None, *args, **kwargs):
        # We are going to pass these args from our django view.
        # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get("url")
        self.domain = kwargs.get("domain")
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]
        self.user_id = user_id
        ArticleSpider.rules = [
            Rule(LinkExtractor(unique=True), callback="parse_item"),
        ]
        super().__init__(*args, **kwargs)

    def start_requests(self):
        url = self.url  # Retrieve the URL passed as an argument
        yield Request(url=url, callback=self.parse, meta={"user_id": self.user_id})

    def parse(self, response, **kwargs):
        user_id = response.meta["user_id"]
        item = ArticleItem()
        title = response.xpath("//h1/text() | //h1/strong/text()").get().strip()
        # exclude_xpath = "//div[@id='root']//descendant-or-self::*"
        html_content = response.body

        item["url"] = self.url
        item["title"] = title
        item["data"] = html_content
        item.instance.user_id = user_id

        yield item
