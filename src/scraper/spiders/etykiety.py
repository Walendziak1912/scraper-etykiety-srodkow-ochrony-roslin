import scrapy

from src.scraper.items import EtykietaItem
from src.scraper.settings import INDEX_URL, is_valid_pdf_filename, sanitize_filename


class EtykietySpider(scrapy.Spider):
    name = "etykiety"
    start_urls = [INDEX_URL]

    def parse(self, response):
        links = response.css("div.title > a::attr(href)").getall()
        self.logger.info("Found %d range pages on index", len(links))
        for href in links:
            yield response.follow(href, callback=self.parse_range)

    def parse_range(self, response):
        range_slug = response.url.rstrip("/").split("/")[-1]
        pdf_count = 0

        for link in response.css("a.file-download"):
            href = link.css("::attr(href)").get()
            if not href or "/attachment/" not in href:
                continue

            extension = (link.css("span.extension::text").get() or "").strip()
            if ".pdf" not in extension.lower():
                continue

            filename = sanitize_filename(extension)
            if not is_valid_pdf_filename(filename):
                continue
            pdf_count += 1
            yield EtykietaItem(
                file_urls=[response.urljoin(href)],
                range=range_slug,
                filename=filename,
                source_page=response.url,
            )

        self.logger.info("Range %s: yielded %d PDF attachments", range_slug, pdf_count)
