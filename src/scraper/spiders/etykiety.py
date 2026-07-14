import scrapy
from scrapy.exceptions import CloseSpider

from src.scraper.cancel import is_cancel_requested
from src.scraper.items import EtykietaItem
from src.scraper.progress import DownloadEvent, emit, progress_enabled
from src.scraper.settings import INDEX_URL, is_valid_pdf_filename, sanitize_filename


class EtykietySpider(scrapy.Spider):
    name = "etykiety"
    start_urls = [INDEX_URL]

    def start_requests(self):
        if progress_enabled():
            emit(
                DownloadEvent(
                    kind="info",
                    message="Wczytywanie strony głównej gov.pl…",
                )
            )
        yield from super().start_requests()

    def parse(self, response):
        if is_cancel_requested():
            raise CloseSpider("cancelled")

        links = response.css("div.title > a::attr(href)").getall()
        self.logger.info("Found %d range pages on index", len(links))
        if progress_enabled():
            emit(
                DownloadEvent(
                    kind="info",
                    message=f"Znaleziono {len(links)} zakresów",    
                )
            )
        for href in links:
            if is_cancel_requested():
                raise CloseSpider("cancelled")
            yield response.follow(href, callback=self.parse_range)

    def parse_range(self, response):
        if is_cancel_requested():
            raise CloseSpider("cancelled")

        range_slug = response.url.rstrip("/").split("/")[-1]
        pdf_count = 0

        for link in response.css("a.file-download"):
            if is_cancel_requested():
                raise CloseSpider("cancelled")

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
        if progress_enabled() and pdf_count:
            emit(
                DownloadEvent(
                    kind="info",
                    message=f"Zakres [{range_slug}]: {pdf_count} plików PDF w kolejce pobierania",
                )
            )
