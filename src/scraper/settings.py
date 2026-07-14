import re

INDEX_URL = "https://www.gov.pl/web/rolnictwo/etykiety-srodkow-ochrony-roslin"

BOT_NAME = "etykiety"
SPIDER_MODULES = ["src.scraper.spiders"]
NEWSPIDER_MODULE = "src.scraper.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.25
USER_AGENT = "scraper-etykiety-srodkow-ochrony-roslin/0.1"

ITEM_PIPELINES = {
    "src.scraper.pipelines.EtykietyFilesPipeline": 1,
    "src.scraper.pipelines.ManifestPipeline": 2,
}

FILES_STORE = ".artifacts/downloads"
MANIFEST_PATH = ""

_ZWSP = "\u200b"
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize_filename(name: str) -> str:
    cleaned = name.replace(_ZWSP, "").strip()
    cleaned = _INVALID_FILENAME_CHARS.sub("_", cleaned)
    return cleaned or "unknown.pdf"


def is_valid_pdf_filename(name: str) -> bool:
    cleaned = sanitize_filename(name)
    if not cleaned.lower().endswith(".pdf"):
        return False
    base = cleaned[:-4]
    return bool(base) and base not in {"@", "unknown"}
