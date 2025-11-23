import logging
import os
from multiprocessing import Lock
from typing import Optional
from datetime import datetime


class Logger:
    """Thread-safe logger with file and console output."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, log_path: str = "logs/hasher.log", verbose: bool = True):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_path: str = "logs/hasher.log", verbose: bool = True):
        if self._initialized:
            return
        
        self.log_path = log_path
        self.verbose = verbose
        self.write_lock = Lock()
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        self.logger = logging.getLogger('HashCracker')
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(processName)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            if verbose:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_formatter = logging.Formatter(
                    '%(levelname)s - %(message)s'
                )
                console_handler.setFormatter(console_formatter)
                self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        with self.write_lock:
            self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        with self.write_lock:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        with self.write_lock:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        with self.write_lock:
            self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        with self.write_lock:
            self.logger.critical(message)
    
    def log_worker_start(self, worker_id: int, chunk_info: str) -> None:
        """Log worker process start."""
        self.info(f"Worker {worker_id} started processing {chunk_info}")
    
    def log_worker_complete(self, worker_id: int, duration: float, items_processed: int) -> None:
        """Log worker process completion."""
        self.info(f"Worker {worker_id} completed: {items_processed} items in {duration:.2f}s")
    
    def log_match_found(self, worker_id: int, original_value: str, hash_value: str) -> None:
        """Log hash match found."""
        self.info(f"Worker {worker_id} FOUND MATCH: {original_value} -> {hash_value}")
    
    def log_pipeline_stats(self, total_time: float, total_items: int, matches_found: int) -> None:
        """Log pipeline statistics."""
        self.info(f"Pipeline completed in {total_time:.2f}s")
        self.info(f"Total items processed: {total_items}")
        self.info(f"Matches found: {matches_found}")
        if total_time > 0:
            self.info(f"Processing rate: {total_items / total_time:.2f} items/sec")
    
    @classmethod
    def get_instance(cls, log_path: str = "logs/hasher.log", verbose: bool = True) -> 'Logger':
        """Get logger singleton instance."""
        if cls._instance is None:
            cls._instance = Logger(log_path, verbose)
        return cls._instance
