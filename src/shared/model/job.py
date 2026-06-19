from argparse import Namespace
from pydantic import BaseModel, ConfigDict, field_validator
import logging
import os

logger = logging.getLogger(__name__)

class JobParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    job_id: str
    log_path: str
    result_path: str

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