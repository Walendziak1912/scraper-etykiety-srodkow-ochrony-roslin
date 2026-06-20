import logging
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from src.core.settings import Settings, get_settings, resolve_download_dir
from src.scraper import settings as scrapy_defaults
from src.scraper.cancel import is_cancel_requested, reset_cancel
from src.scraper.progress import DownloadEvent, emit
from src.shared.model.job import JobParams


def _result_dir(result_path: str) -> Path:
    path = Path(result_path)
    return path.parent if path.suffix else path


def build_scrapy_settings(
    job: JobParams,
    app_settings: Settings | None = None,
) -> dict:
    app_settings = app_settings or get_settings()
    download_dir = resolve_download_dir(app_settings.download_dir)
    if download_dir is None:
        raise ValueError("DOWNLOAD_DIR nie jest ustawiony.")
    download_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = ""
    if app_settings.manifest_enabled:
        path = _result_dir(job.result_path) / "manifest.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path = str(path)

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
        "MANIFEST_PATH": manifest_path,
        "LOG_LEVEL": "INFO",
        "EXTENSIONS": {
            "src.scraper.cancel.CancelControllerExtension": 50,
        },
    }


def run_scraper(
    job: JobParams,
    logger: logging.Logger | None = None,
    *,
    download_dir: Path | str | None = None,
    track_progress: bool = False,
) -> dict:
    app_settings = get_settings()
    if download_dir is not None:
        app_settings = app_settings.model_copy(update={"download_dir": str(Path(download_dir))})

    reset_cancel()

    if track_progress:
        emit(
            DownloadEvent(
                kind="started",
                message=f"Rozpoczęto pobieranie etykiet PDF do: {resolve_download_dir(app_settings.download_dir)}",
            )
        )

    scrapy_settings = build_scrapy_settings(job, app_settings)
    if logger:
        scrapy_settings["LOG_LEVEL"] = logging.getLevelName(logger.level)

    process = CrawlerProcess(scrapy_settings)
    crawler = process.create_crawler("etykiety")
    process.crawl(crawler)
    process.start()

    stats = crawler.stats.get_stats()
    result = {
        "item_scraped_count": stats.get("item_scraped_count", 0),
        "downloader/response_count": stats.get("downloader/response_count", 0),
        "file_status_count/downloaded": stats.get("file_status_count/downloaded", 0),
        "file_status_count/uptodate": stats.get("file_status_count/uptodate", 0),
        "log_count/ERROR": stats.get("log_count/ERROR", 0),
        "cancelled": is_cancel_requested(),
    }

    if track_progress:
        if is_cancel_requested():
            emit(
                DownloadEvent(
                    kind="cancelled",
                    message="Pobieranie przerwane przez użytkownika.",
                    stats=result,
                )
            )
        else:
            emit(
                DownloadEvent(
                    kind="finished",
                    message="Pobieranie zakończone.",
                    stats=result,
                )
            )

    reset_cancel()
    return result


def main() -> None:
    from src.shared.model.job import set_job_params

    job = JobParams.create_default()
    set_job_params(job)
    stats = run_scraper(job)
    print(stats)


if __name__ == "__main__":
    main()
