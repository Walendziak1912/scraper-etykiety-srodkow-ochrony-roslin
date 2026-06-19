"""Quick verification helpers for gov.pl scraper."""

import json
import re
import urllib.request
from pathlib import Path

INDEX_URL = "https://www.gov.pl/web/rolnictwo/etykiety-srodkow-ochrony-roslin"
AB_URL = "https://www.gov.pl/web/rolnictwo/a-b1"


def count_index_links() -> int:
    html = urllib.request.urlopen(INDEX_URL).read().decode("utf-8")
    return len(re.findall(r'<div class="title">\s*<a href="([^"]+)"', html))


def count_ab_pdfs() -> int:
    html = urllib.request.urlopen(AB_URL).read().decode("utf-8")
    count = 0
    for block in re.findall(r'<a class="file-download"[^>]*>.*?</a>', html, re.S):
        ext_match = re.search(r'<span class="extension">([^<]+)</span>', block)
        if not ext_match:
            continue
        ext = ext_match.group(1).replace("\u200b", "")
        if ext.lower().endswith(".pdf") and ext not in {"@.pdf", "@&#8203;.pdf"}:
            count += 1
    return count


def verify_downloads(download_dir: Path) -> dict:
    pdfs = list(download_dir.rglob("*.pdf"))
    valid = 0
    for pdf in pdfs[:20]:
        if pdf.read_bytes()[:4] == b"%PDF":
            valid += 1
    manifest = download_dir / "manifest.jsonl"
    manifest_lines = 0
    if manifest.exists():
        manifest_lines = sum(1 for _ in manifest.open(encoding="utf-8"))
    return {
        "pdf_files": len(pdfs),
        "valid_pdf_headers_sample": valid,
        "manifest_lines": manifest_lines,
    }


if __name__ == "__main__":
    print("index_links:", count_index_links())
    print("a-b1_pdfs:", count_ab_pdfs())
    print("downloads:", verify_downloads(Path(".artifacts/downloads-test")))
