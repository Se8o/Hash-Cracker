"""
Parallel Hash Cracking Engine - Task Queue Module

Author: Sebastian Lodin
Date: November 2025
Description: Thread-safe task queue implementation using multiprocessing.Queue
"""

from multiprocessing import Queue as MPQueue
from typing import Any, Optional
from src.pipeline.logger import Logger


class TaskQueue:
    """Thread-safe task queue using multiprocessing.Queue."""
    
    POISON_PILL = None
    
    def __init__(self):
        self.queue = MPQueue()
        self.logger = Logger.get_instance()
        self.tasks_added = 0
        self.tasks_completed = 0
    
    def put(self, task: Any) -> None:
        """
        Add task to queue.
        
        Args:
            task: Task data to add
        """
        self.queue.put(task)
        self.tasks_added += 1
    
    def get(self, timeout: Optional[float] = None) -> Any:
        """
        Get task from queue.
        
        Args:
            timeout: Optional timeout in seconds
        
        Returns:
            Task data or POISON_PILL
        """
        try:
            task = self.queue.get(timeout=timeout)
            if task is not self.POISON_PILL:
                self.tasks_completed += 1
            return task
        except Exception as e:
            self.logger.error(f"Error getting task from queue: {e}")
            return self.POISON_PILL
    
    def put_many(self, tasks: list) -> None:
        """
        Add multiple tasks to queue.
        
        Args:
            tasks: List of tasks to add
        """
        for task in tasks:
            self.put(task)
        
        self.logger.debug(f"Added {len(tasks)} tasks to queue")
    
    def send_poison_pills(self, num_workers: int) -> None:
        """
        Send poison pills to terminate workers.
        
        Args:
            num_workers: Number of workers to terminate
        """
        for _ in range(num_workers):
            self.queue.put(self.POISON_PILL)
        
        self.logger.debug(f"Sent {num_workers} poison pills")
    
    def size(self) -> int:
        """
        Get approximate queue size.
        
        Returns:
            Queue size
        """
        return self.queue.qsize()
    
    def is_empty(self) -> bool:
        """
        Check if queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        return self.queue.empty()
    
    def get_statistics(self) -> dict:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'tasks_added': self.tasks_added,
            'tasks_completed': self.tasks_completed,
            'current_size': self.size()
        }
