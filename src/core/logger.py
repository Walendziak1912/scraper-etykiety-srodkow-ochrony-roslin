import logging
from datetime import datetime
from pathlib import Path
from src.core.settings import get_settings
from src.shared.model.job import JobParams

def configure_logger(job_params : JobParams) -> logging.Logger:
    settings = get_settings()  
    
    logger_name = settings.logger_name
    logger = logging.getLogger(logger_name)
    
    path = job_params.log_path
    log_dir = Path(path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filename = Path(path).name
    log_file_path = log_dir / log_filename
    
    logger = logging.getLogger(logger_name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    logger.propagate = False 
    
    logger.handlers.clear()
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    _lvl_name = (settings.console_log_level or "INFO").strip().upper()
    console_handler.setLevel(getattr(logging, _lvl_name, logging.INFO))
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    #logger.addHandler(console_handler)
    
    _logger = logger
    logger.info(f'Logger zainicjalizowany. Logi zapisywane do: {log_file_path}')
    return logger
