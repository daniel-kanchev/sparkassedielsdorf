import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sparkassedielsdorf.items import Article


class SparkassedielsdorfSpider(scrapy.Spider):
    name = 'sparkassedielsdorf'
    start_urls = ['https://sparkasse-dielsdorf.ch/de/News']

    def parse(self, response):
        articles = response.xpath('//div[@class="newscol col-md-4"]')
        for article in articles:
            link = article.xpath('./div[@class="news-image"]/a/@href').get()
            date = article.xpath('./div[@class="news-info"]//text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2//text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="col-sm-9"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
