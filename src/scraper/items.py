import scrapy


class EtykietaItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()
    range = scrapy.Field()
    filename = scrapy.Field()
    source_page = scrapy.Field()
    download_status = scrapy.Field()
    download_errors = scrapy.Field()
