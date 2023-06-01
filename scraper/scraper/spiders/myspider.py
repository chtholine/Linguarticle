import re
from typing import NamedTuple
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import scrapy
from scrapy_splash import SplashRequest

from ..items import ArticleItem


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
        yield SplashRequest(url=url, callback=self.parse, args={"wait": 0.5}, meta={"user_id": self.user_id})

    def parse(self, response, **kwargs):
        user_id = response.meta["user_id"]
        item = ArticleItem()
        title = response.xpath("//h1/text() | //h1/strong/text()").get().strip()
        title_data = map_text(title, Style.H1)
        author = response.xpath("//p/a[contains(@rel, 'noopener') and contains(@rel, 'follow')]/text()").get()
        author_data = map_text(author, Style.H2)
        data = response.xpath("//section/descendant::*[not(self::style)]//text()").getall()
        content = " ".join([text.strip() for text in data if text.strip() not in (title, author)])
        # for element in response.xpath("//section/descendant::*[not(self::style)]"):
        #     text = element.xpath("text()").get()
        #     if text is not None and text.strip() not in (title, author):
        #         tag = element.xpath("name()").get().upper()
        #         tag = tag if tag in Style.__dict__.values() else Style.P
        #         data.extend(map_text(text, tag))

        item["url"] = self.url
        item["title"] = title
        item["author"] = author
        item["data"] = content
        item.instance.user_id = user_id

        yield item
