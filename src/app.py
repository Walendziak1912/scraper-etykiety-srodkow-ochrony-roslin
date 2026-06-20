import logging
import multiprocessing as mp
from multiprocessing.queues import Queue as MpQueue
from pathlib import Path

from src.core.logger import configure_logger
from src.core.settings import get_settings, resolve_download_dir
from src.scraper.runner import run_scraper
from src.scraper.worker import run_scraper_process
from src.shared.exceptions import AppError
from src.shared.model.job import JobParams
from src.utils.io import save_result_to_jsonlines

settings = get_settings()


def _result_dir(result_path: str) -> Path:
    path = Path(result_path)
    return path.parent if path.suffix else path


class App:
    def __init__(
        self,
        job: JobParams,
        *,
        download_dir: Path | str | None = None,
    ) -> None:
        self.job = job
        self.download_dir = (
            Path(download_dir)
            if download_dir
            else resolve_download_dir(settings.download_dir) or Path(".")
        )
        self.logger = configure_logger(job)
        self.logger.info("App initialized with job ID: %s", job.job_id)
        self.logger.info("Download directory: %s", self.download_dir)

    def run(self, *, track_progress: bool = False) -> int:
        try:
            self.logger.info("Starting the application...")
            stats = run_scraper(
                self.job,
                self.logger,
                download_dir=self.download_dir,
                track_progress=track_progress,
            )
            result = {"status": "success", "job_id": self.job.job_id, **stats}
            summary_path = _result_dir(self.job.result_path) / "summary.jsonl"
            save_result_to_jsonlines(result, summary_path)
            self.logger.info("Application finished successfully. Stats: %s", stats)
            return 0
        except AppError as e:
            self.logger.error("AppError occurred: %s", e)
            return 1
        except Exception as e:
            self.logger.error("An error occurred: %s", e)
            return 1


class AppRunner:
    def __init__(self, download_dir: Path | str) -> None:
        self.download_dir = Path(download_dir)
        self._process: mp.Process | None = None
        self._queue: MpQueue | None = None
        self._killed = False

    @property
    def progress_queue(self) -> MpQueue | None:
        return self._queue

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.is_alive()

    @property
    def was_killed(self) -> bool:
        return self._killed

    def start(self) -> None:
        if self.is_running:
            return

        self._queue = mp.Queue()
        self._killed = False
        self._process = mp.Process(
            target=run_scraper_process,
            args=(str(self.download_dir), self._queue),
            daemon=True,
            name="scraper-worker",
        )
        self._process.start()

    def cancel(self) -> None:
        if not self.is_running:
            return

        self._killed = True
        self._process.terminate()
        self._process.join(timeout=2)
        if self._process.is_alive():
            self._process.kill()
            self._process.join(timeout=2)

    def join(self, timeout: float | None = None) -> None:
        if self._process is not None:
            self._process.join(timeout=timeout)

    def is_alive(self) -> bool:
        return self.is_running


def create_default_job() -> JobParams:
    return JobParams.create_default()
