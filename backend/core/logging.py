"""
Sherlock.ai - Logging Configuration
Structured logging for production-ready applications
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """
    Configure application logging with console and file handlers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("sherlock")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Format
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            file_path = log_dir / log_file
        else:
            file_path = Path(log_file)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "sherlock") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
