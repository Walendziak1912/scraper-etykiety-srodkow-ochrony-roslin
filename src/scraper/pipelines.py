from pathlib import Path

from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline

from src.utils.io import save_result_to_jsonlines


class EtykietyFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        adapter = ItemAdapter(item)
        range_slug = adapter.get("range") or "unknown"
        filename = adapter.get("filename") or "unknown.pdf"
        return f"{range_slug}/{filename}"

    def item_completed(self, results, item, info):
        adapter = ItemAdapter(item)
        ok, failed = [], []
        for success, result in results:
            if success:
                ok.append(result)
            else:
                failed.append(result)

        adapter["files"] = ok
        adapter["download_status"] = "downloaded" if ok else "failed"
        if failed:
            adapter["download_errors"] = failed
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
