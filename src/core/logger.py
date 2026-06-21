import logging
from pathlib import Path

from src.core.settings import Settings, get_settings
from src.shared.enums import LogType
from src.shared.model.job import JobParams

FILE_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILE_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
CONSOLE_LOG_FORMAT = "%(levelname)s - %(message)s"


def _resolve_log_level(level_name: str, default: int = logging.INFO) -> int:
    return getattr(logging, (level_name or "").strip().upper(), default)


def _create_console_handler(settings: Settings) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setLevel(_resolve_log_level(settings.console_log_level))
    handler.setFormatter(logging.Formatter(CONSOLE_LOG_FORMAT))
    return handler

def _resolve_log_file_path(job_params: JobParams) -> Path:
    log_dir = Path(job_params.log_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / Path(job_params.log_path).name


def _create_file_handler(log_file_path: Path) -> logging.Handler:
    handler = logging.FileHandler(log_file_path, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(FILE_LOG_FORMAT, datefmt=FILE_LOG_DATEFMT)
    )
    return handler


def _attach_file_handler(logger: logging.Logger, job_params: JobParams) -> Path:
    log_file_path = _resolve_log_file_path(job_params)
    logger.addHandler(_create_file_handler(log_file_path))
    return log_file_path


def configure_logger(job_params: JobParams) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(settings.logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()

    log_types = job_params.log_types

    if LogType.CONSOLE in log_types:
        logger.addHandler(_create_console_handler(settings))

    log_file_path: Path | None = None
    if LogType.FILE in log_types:
        log_file_path = _attach_file_handler(logger, job_params)

    if LogType.CONSOLE in log_types and LogType.FILE in log_types:
        logger.info("Logger zainicjalizowany. Logi zapisywane do: %s", log_file_path)
    elif LogType.FILE in log_types:
        logger.info("Logger zainicjalizowany tylko plik. Logi zapisywane do: %s", log_file_path)
    elif LogType.CONSOLE in log_types:
        logger.info("Logger zainicjalizowany tylko konsola.")
    else:
        logger.warning("Logger zainicjalizowany bez handlerów")
    return logger
