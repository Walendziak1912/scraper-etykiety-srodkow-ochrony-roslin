import logging
from pathlib import Path
from src.core.logger import configure_logger
from src.core.settings import get_settings
from src.utils.io import save_result_to_jsonlines
from src.shared.model.job import JobParams
from src.shared.exceptions import AppError
from src.scraper.runner import run_scraper

settings = get_settings()


def _result_dir(result_path: str) -> Path:
    path = Path(result_path)
    return path.parent if path.suffix else path


class App:
    def __init__(self, job: JobParams) -> None:
        self.job = job
        self.logger = configure_logger(job)
        self.logger.info(f"App initialized with job ID: {job.job_id}")

    def run(self):
        try:
            self.logger.info("Starting the application...")
            stats = run_scraper(self.job, self.logger)
            result = {"status": "success", "job_id": self.job.job_id, **stats}
            summary_path = _result_dir(self.job.result_path) / "summary.jsonl"
            save_result_to_jsonlines(result, summary_path)
            self.logger.info("Application finished successfully. Stats: %s", stats)
            return 0
        except AppError as e:
            self.logger.error(f"AppError occurred: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return 1
