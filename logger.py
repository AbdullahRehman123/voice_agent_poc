# logger.py
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


def setup_logger() -> logging.Logger:
    """
    Returns a logger that writes to a daily-rotated file with timestamp-based filename.
    Keeps up to 30 days of log history.
    """
    # Create logs/ folder if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Datetime-stamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"logs/{timestamp}.log"

    # Create logger
    logger = logging.getLogger("voice_agent")
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding multiple handlers if called multiple times
    if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
        # Daily rotating file handler
        file_handler = TimedRotatingFileHandler(
            filename=log_filename,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        
        logger.addHandler(file_handler)
        
        # Log session start
        logger.info("=" * 60)
        logger.info(f"Session Started: {timestamp}")
        logger.info("=" * 60)
        
        print(f"📋 Logging to: {log_filename}")

    return logger