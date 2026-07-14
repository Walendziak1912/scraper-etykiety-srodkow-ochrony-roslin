from __future__ import annotations

from pathlib import Path

from src.scraper.progress import init_progress_queue
from src.shared.model.job import JobParams, set_job_params


def run_scraper_process(download_dir: str, event_queue) -> int:
    from src.app import App

    init_progress_queue(event_queue)

    job = JobParams.create_default()
    set_job_params(job)
    app = App(job, download_dir=Path(download_dir))
    return app.run(track_progress=True)
