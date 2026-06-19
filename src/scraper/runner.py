import logging
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from src.core.settings import Settings, get_settings
from src.scraper import settings as scrapy_defaults
from src.shared.model.job import JobParams
from src.scraper import settings as scrapy_defaults
from src.shared.model.job import JobParams


def _result_dir(result_path: str) -> Path:
    path = Path(result_path)
    return path.parent if path.suffix else path


def build_scrapy_settings(
    job: JobParams,
    app_settings: Settings | None = None,
) -> dict:
    app_settings = app_settings or get_settings()
    download_dir = Path(app_settings.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = _result_dir(job.result_path) / "manifest.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    return {
        "BOT_NAME": scrapy_defaults.BOT_NAME,
        "SPIDER_MODULES": scrapy_defaults.SPIDER_MODULES,
        "NEWSPIDER_MODULE": scrapy_defaults.NEWSPIDER_MODULE,
        "ROBOTSTXT_OBEY": scrapy_defaults.ROBOTSTXT_OBEY,
        "CONCURRENT_REQUESTS": app_settings.scrapy_concurrent_requests,
        "DOWNLOAD_DELAY": app_settings.scrapy_download_delay,
        "USER_AGENT": scrapy_defaults.USER_AGENT,
        "ITEM_PIPELINES": scrapy_defaults.ITEM_PIPELINES,
        "FILES_STORE": str(download_dir.resolve()),
        "MANIFEST_PATH": str(manifest_path),
        "LOG_LEVEL": "INFO",
    }


def run_scraper(job: JobParams, logger: logging.Logger | None = None) -> dict:
    scrapy_settings = build_scrapy_settings(job)
    if logger:
        scrapy_settings["LOG_LEVEL"] = logging.getLevelName(logger.level)

    process = CrawlerProcess(scrapy_settings)
    crawler = process.create_crawler("etykiety")
    process.crawl(crawler)
    process.start()

    stats = crawler.stats.get_stats()
    return {
        "item_scraped_count": stats.get("item_scraped_count", 0),
        "downloader/response_count": stats.get("downloader/response_count", 0),
        "file_status_count/downloaded": stats.get("file_status_count/downloaded", 0),
        "file_status_count/uptodate": stats.get("file_status_count/uptodate", 0),
        "log_count/ERROR": stats.get("log_count/ERROR", 0),
    }


def main() -> None:
    import uuid
    from datetime import datetime

    from src.shared.model.job import set_job_params

    today = datetime.now().strftime("%Y-%m-%d")
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    job = JobParams(
        job_id=str(uuid.uuid4()),
        log_path=f".artifacts/logs/{today}/{stamp}.log",
        result_path=f".artifacts/logs/{today}/{stamp}/manifest.jsonl",
    )
    set_job_params(job)
    stats = run_scraper(job)
    print(stats)


if __name__ == "__main__":
    main()
