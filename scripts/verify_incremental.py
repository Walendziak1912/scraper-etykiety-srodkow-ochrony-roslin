import uuid
from datetime import datetime
from pathlib import Path

from src.scraper.runner import build_scrapy_settings, run_scraper
from src.shared.model.job import JobParams, set_job_params

store = Path(".artifacts/downloads-test")
manifest_dir = Path(".artifacts/logs/verify-incremental")
manifest_dir.mkdir(parents=True, exist_ok=True)

before = len(list(store.rglob("*.pdf")))

job = JobParams(
    job_id=str(uuid.uuid4()),
    log_path=str(manifest_dir / "run.log"),
    result_path=str(manifest_dir),
)
set_job_params(job)

settings = build_scrapy_settings(job)
settings["FILES_STORE"] = str(store.resolve())
settings["CLOSESPIDER_ITEMCOUNT"] = 3
settings["LOG_LEVEL"] = "ERROR"

from scrapy.crawler import CrawlerProcess

process = CrawlerProcess(settings)
crawler = process.create_crawler("etykiety")
process.crawl(crawler)
process.start()

stats = crawler.stats.get_stats()
after = len(list(store.rglob("*.pdf")))

print(
    {
        "downloaded": stats.get("file_status_count/downloaded", 0),
        "uptodate": stats.get("file_status_count/uptodate", 0),
        "pdf_before": before,
        "pdf_after": after,
    }
)
