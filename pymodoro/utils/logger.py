import logging
import os
import sys
from pathlib import Path
from typing import Optional

MAX_LOG_SIZE = 50 * 1024  # 50KB

def setup_logger(name="pymodoro", level=logging.INFO, log_file: Optional[str] = None, clear_log: bool = True):
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Custom log file path (optional)
        clear_log: Whether to clear the log file at startup
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Determine log file location
    if log_file:
        log_path = Path(log_file)
    else:
        log_dir = Path.home() / ".config" / "pymodoro" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "pymodoro.log"
    
    # Check log file size and truncate if too large
    if log_path.exists() and log_path.stat().st_size > MAX_LOG_SIZE:
        # Keep only the last 25KB (half the limit)
        with open(log_path, 'rb') as f:
            f.seek(-25 * 1024, 2)  # Seek to 25KB from end
            content = f.read()
        
        with open(log_path, 'wb') as f:
            f.write(b'\n--- LOG TRUNCATED ---\n')
            f.write(content)
    
    # Clear log file at startup if requested
    if clear_log and log_path.exists():
        log_path.unlink()
    
    # File handler for persistent logging
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup info
    logger.info(f"Pymodoro logging initialized - log file: {log_path}")
    logger.debug(f"Console log level: {logging.getLevelName(level)}")
    logger.debug(f"File log level: DEBUG")
    logger.debug(f"Max log size: {MAX_LOG_SIZE // 1024}KB")
    
    return logger

def get_logger(name: str = "pymodoro") -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)

def log_exception(logger: logging.Logger, message: str, exc_info=True):
    """Helper to log exceptions with context"""
    logger.error(f"{message}", exc_info=exc_info)

def parse_log_level(level_str: str) -> int:
    """Parse log level string to logging constant"""
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return level_map.get(level_str.upper(), logging.INFO) 