import logging
from logging.handlers import RotatingFileHandler
import os

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE_NAME = "app.log"
LINK_LOG_FILE_NAME = "match_links.log"


def setup_link_logger(log_dir: str = DEFAULT_LOG_DIR):
    """Sets up a dedicated logger for match links."""
    link_logger = logging.getLogger("LinkLogger")
    link_logger.setLevel(logging.INFO)

    # Prevent link logs from propagating to the root logger
    link_logger.propagate = False

    links_log_dir = os.path.join(log_dir)
    os.makedirs(links_log_dir, exist_ok=True)
    log_file_path = os.path.join(links_log_dir, LINK_LOG_FILE_NAME)

    # Use a simple formatter for links
    formatter = logging.Formatter("%(message)s")

    # Use a rotating file handler for the link logger
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1 * 1024 * 1024, backupCount=3)  # 1 MB
    file_handler.setFormatter(formatter)

    # Add handler only if not already present
    if not link_logger.handlers:
        link_logger.addHandler(file_handler)


def setup_logger(
    log_level: int = logging.INFO,
    save_to_file: bool = False,
    log_file: str = DEFAULT_LOG_FILE_NAME,
    log_dir: str = DEFAULT_LOG_DIR,
    max_file_size: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5,
):
    """
    Sets up logging for both console and optionally file output.

    Args:
        log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
        save_to_file (bool): Whether to save logs to a file.
        log_file (str): The name of the log file.
        log_dir (str): Directory where log files will be stored.
        max_file_size (int): Maximum size of a single log file in bytes.
        backup_count (int): Number of backup log files to retain.
    """
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    handlers = [console_handler]

    if save_to_file:
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, log_file)
        file_handler = RotatingFileHandler(log_file_path, maxBytes=max_file_size, backupCount=backup_count)
        file_handler.setFormatter(log_formatter)
        handlers.append(file_handler)

        logging.basicConfig(level=log_level, handlers=handlers)
        logging.info(f"Logging initialized. Log level: {logging.getLevelName(log_level)}")

        if save_to_file:
            logging.info(f"Logs will be saved to {log_file_path}")
    else:
        logging.basicConfig(level=log_level, handlers=handlers)
        logging.info(f"Logging initialized. Log level: {logging.getLevelName(log_level)} (No file output)")

    # Setup the dedicated logger for match links
    setup_link_logger(log_dir=log_dir)
    logging.info(f"Match links will be saved to {os.path.join(log_dir, LINK_LOG_FILE_NAME)}")
