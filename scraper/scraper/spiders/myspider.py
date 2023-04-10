import re
from time import sleep
from typing import NamedTuple
from .. import items
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import scrapy

from ..items import ArticleItem


# scrapy runspider myspider.py -O article.json


class Style(NamedTuple):
    P = "P"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"
    H6 = "H6"
    STRONG = "STRONG"


class Format(NamedTuple):
    WORD = "WORD"
    SPACE = "SPACE"
    SIGN = "SIGN"


def map_text(text, tag):
    words = re.findall(r"(?:\w+(?:[^\w\s]+\w+)*)|\w+|\s|[^\w\s]+", text, re.UNICODE)
    return [
        {"Text": word, "Tag": tag, "Format": Format.SPACE}
        if word.isspace()
        else {
            "Text": word,
            "Tag": tag,
            "Format": Format.WORD if re.search(r"\w(?:\W+\w+)*|\w+", word) else Format.SIGN,
        }
        for word in words
    ]


class ArticleSpider(scrapy.Spider):
    name = "article_spider"

    def __init__(self, *args, **kwargs):
        # We are going to pass these args from our django view.
        # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get("url")
        self.domain = kwargs.get("domain")
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]

        ArticleSpider.rules = [
            Rule(LinkExtractor(unique=True), callback="parse_item"),
        ]
        super(ArticleSpider, self).__init__(*args, **kwargs)

    # allowed_domains = ["*"]
    # start_urls = ["https://medium.com/@schopade333/django-best-practices-a95f9b2b11e8"]

    def parse(self, response, **kwargs):
        sleep(5)
        item = ArticleItem()

        url = response.request.url
        title = response.xpath("//h1/text() | //h1/strong/text()").get().strip()
        title_data = map_text(title, Style.H1)
        author = response.xpath("//a/span/text() | //h2/span/text()").get().strip()
        author_data = map_text(author, Style.H2)
        data = []
        for element in response.xpath("//section/descendant::*[not(self::style)]"):
            text = element.xpath("text()").get()
            if text is not None and text.strip() not in (title, author):
                tag = element.xpath("name()").get().upper()
                tag = tag if tag in Style.__dict__.values() else Style.P
                data.extend(map_text(text, tag))

        item["url"] = url
        item["title"] = title_data
        item["author"] = author_data
        item["data"] = data

        yield item
