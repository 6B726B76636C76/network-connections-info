import logging
import logging.handlers
import os
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger(
    name: str = 'sys-info',
    log_file: str = 'logs/sysinfo-service.log',
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    max_mb: int = 30,
    backup_count: int = 33

) -> logging.Logger:

    global _logger

    if _logger is not None:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(min(console_level, file_level))
    _logger.propagate = False

    formatter = logging.Formatter(
        '| %(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


logger = get_logger(
    max_mb=30,
    backup_count=33
)
