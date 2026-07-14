from __future__ import annotations

import threading

from scrapy.crawler import Crawler

_cancel_event = threading.Event()
_active_crawler: Crawler | None = None
_lock = threading.Lock()


def reset_cancel() -> None:
    _cancel_event.clear()
    with _lock:
        global _active_crawler
        _active_crawler = None


def register_crawler(crawler: Crawler) -> None:
    with _lock:
        global _active_crawler
        _active_crawler = crawler


def is_cancel_requested() -> bool:
    return _cancel_event.is_set()


def request_cancel() -> None:
    if _cancel_event.is_set():
        return

    _cancel_event.set()

    with _lock:
        crawler = _active_crawler

    def _stop() -> None:
        if crawler is not None and crawler.spider is not None:
            crawler.engine.close_spider(crawler.spider, "cancelled")
        from twisted.internet import reactor

        if reactor.running:
            reactor.stop()

    try:
        from twisted.internet import reactor

        if reactor.running:
            reactor.callFromThread(_stop)
    except Exception:
        pass


class CancelControllerExtension:
    @classmethod
    def from_crawler(cls, crawler):
        register_crawler(crawler)
        return cls()
