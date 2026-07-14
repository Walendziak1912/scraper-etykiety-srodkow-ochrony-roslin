from pathlib import Path

from itemadapter import ItemAdapter
from scrapy.exceptions import CloseSpider
from scrapy.pipelines.files import FilesPipeline

from src.scraper.cancel import is_cancel_requested
from src.scraper.progress import DownloadEvent, emit, progress_enabled
from src.utils.io import save_result_to_jsonlines


class EtykietyFilesPipeline(FilesPipeline):
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = super().from_crawler(crawler)
        pipeline.download_root = Path(crawler.settings.get("FILES_STORE", "."))
        return pipeline

    def file_path(self, request, response=None, info=None, *, item=None):
        adapter = ItemAdapter(item)
        range_slug = adapter.get("range") or "unknown"
        filename = adapter.get("filename") or "unknown.pdf"
        return f"{range_slug}/{filename}"

    def process_item(self, item, spider):
        if is_cancel_requested():
            raise CloseSpider("cancelled")
        return super().process_item(item, spider)

    def item_completed(self, results, item, info):
        adapter = ItemAdapter(item)
        ok, failed = [], []
        for success, result in results:
            if success:
                ok.append(result)
            else:
                failed.append(result)

        adapter["files"] = ok
        if ok:
            file_status = ok[0].get("status", "downloaded")
            adapter["download_status"] = file_status
        else:
            adapter["download_status"] = "failed"
        if failed:
            adapter["download_errors"] = failed

        if progress_enabled() and ok:
            rel_path = ok[0].get("path", "")
            file_status = ok[0].get("status", "downloaded")
            full_path = (self.download_root / rel_path).resolve()
            range_slug = str(adapter.get("range") or "")
            filename = str(adapter.get("filename") or "")
            if file_status == "uptodate":
                message = ""
            elif file_status == "downloaded":
                message = f"Zapisano: {full_path}"
                emit(
                    DownloadEvent(
                        kind="downloading",
                        range_slug=range_slug,
                        filename=filename,
                        message=f"Pobieranie [{range_slug}]: {filename}",
                    )
                )
            else:
                message = f"Zapisano: {full_path}"
            emit(
                DownloadEvent(
                    kind="file",
                    range_slug=range_slug,
                    filename=filename,
                    stored_path=str(full_path),
                    status=file_status,
                    message=message,
                )
            )
        elif progress_enabled() and failed:
            range_slug = str(adapter.get("range") or "")
            filename = str(adapter.get("filename") or "")
            emit(
                DownloadEvent(
                    kind="file",
                    range_slug=range_slug,
                    filename=filename,
                    status="failed",
                    message=f"Błąd pobierania [{range_slug}]: {filename}",
                )
            )

        return item


class ManifestPipeline:
    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path

    @classmethod
    def from_crawler(cls, crawler):
        return cls(manifest_path=crawler.settings.get("MANIFEST_PATH", ""))

    def process_item(self, item):
        if not self.manifest_path:
            return item

        adapter = ItemAdapter(item)
        file_info = adapter.get("files") or []
        stored_path = file_info[0]["path"] if file_info else None

        save_result_to_jsonlines(
            {
                "range": adapter.get("range"),
                "filename": adapter.get("filename"),
                "source_page": adapter.get("source_page"),
                "file_urls": adapter.get("file_urls"),
                "stored_path": stored_path,
                "status": adapter.get("download_status", "unknown"),
            },
            Path(self.manifest_path),
        )
        return item
