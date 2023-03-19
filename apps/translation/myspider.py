import re
from typing import NamedTuple

import scrapy

# scrapy runspider myspider article.json

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
    data = []
    for word in words:
        if word.isspace():
            data.append({"Text": word, "Tag": tag, "Format": Format.SPACE})
        else:
            data.append(
                {
                    "Text": word,
                    "Tag": tag,
                    "Format": Format.WORD
                    if word.isalnum()
                    else Format.SIGN,
                }
            )
    return data


class ArticleSpider(scrapy.Spider):
    name = "article"
    allowed_domains = ["*"]
    start_urls = [
        "https://medium.com/@schopade333/django-best-practices-a95f9b2b11e8"
    ]

    def parse(self, response, **kwargs):
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
        yield {"title": title_data, "author": author_data, "data": data, "url": response.url}
