from scrapy.exceptions import DropItem
from apps.translation.models import Article


class ScraperPipeline:
    def process_item(self, item, spider):
        url = item["url"]
        if Article.objects.filter(url=url).exists():
            article = Article.objects.get(url=url)
            article.user.add(spider.user_id)
            article.save()
            raise DropItem(f"Existing article found. User added to the article: {url}")

        article = Article.objects.create(url=url)
        article.user.add(spider.user_id)
        article.title = item["title"]
        article.author = item["author"]
        article.data = item["data"]
        article.save()
        return item
