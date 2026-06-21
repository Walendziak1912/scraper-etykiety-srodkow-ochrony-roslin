from argparse import Namespace
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
import logging
import os
import uuid

from src.shared.enums import LogType

logger = logging.getLogger(__name__)

class JobParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    job_id: str
    log_path: str
    result_path: str
    log_types: list[LogType] = Field(
        default_factory=lambda: [LogType.CONSOLE]
        #default_factory=lambda: [LogType.CONSOLE, LogType.FILE]
    )

    @field_validator("log_path", "result_path", mode="before")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        if not isinstance(v, str) or not v:
            return v
        if len(v) - len(v.lstrip("\\")) > 2:
            v = "\\\\" + v.lstrip("\\")
        return os.path.normpath(v)

    @staticmethod
    def from_args(args: Namespace) -> "JobParams":
        return JobParams(
            job_id=args.job_id,
            log_path=args.log_path,
            result_path=args.result_path,
        )

    @classmethod
    def create_default(cls) -> "JobParams":
        from src.core.settings import get_settings

        logs_root = Path(get_settings().logs_dir)
        today = datetime.now().strftime("%Y-%m-%d")
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return cls(
            job_id=str(uuid.uuid4()),
            log_path=str(logs_root / today / f"{stamp}.log"),
            result_path=str(logs_root / today / stamp / "manifest.jsonl"),
        )


_JOB_PARAMS: JobParams | None = None

def set_job_params(job: JobParams) -> None:
    global _JOB_PARAMS
    _JOB_PARAMS = job

def get_job_params() -> JobParams:
    if _JOB_PARAMS is None:
        raise RuntimeError("Job parameters are not initialized. Call set_job_params() first.")
    return _JOB_PARAMS

def log_params() -> None:
    if _JOB_PARAMS is not None:
        logger.info("JobParams: %s", _JOB_PARAMS.model_dump())
    else:
        logger.warning("JobParams are not set.")

def clear_job_params() -> None:
    global _JOB_PARAMS
    _JOB_PARAMS = None