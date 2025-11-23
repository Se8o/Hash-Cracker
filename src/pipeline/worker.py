from multiprocessing import Process
from typing import Dict, Any, List
from src.pipeline.hasher import Hasher
from src.pipeline.task_queue import TaskQueue
from src.pipeline.logger import Logger
from src.utils.timer import Timer


class Worker(Process):
    """Worker process for parallel hash computation and comparison."""
    
    def __init__(self, worker_id: int, task_queue: TaskQueue, results_dict: dict,
                 target_hash: str, config: Dict[str, Any]):
        super().__init__()
        
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.results_dict = results_dict
        self.target_hash = target_hash.lower()
        self.config = config
        
        self.algorithm = config['hash']['algorithm']
        self.iterations = config['hash'].get('pbkdf2_iterations', 100000)
        self.salt_length = config['hash'].get('pbkdf2_salt_length', 32)
        
        self.items_processed = 0
        self.matches_found = 0
    
    def run(self) -> None:
        """Main worker process loop."""
        logger = Logger.get_instance(
            self.config['output']['log_path'],
            self.config['output']['verbose']
        )
        
        hasher = Hasher(
            algorithm=self.algorithm,
            iterations=self.iterations,
            salt_length=self.salt_length
        )
        
        logger.log_worker_start(self.worker_id, "waiting for tasks")
        timer = Timer()
        timer.start()
        
        while True:
            task = self.task_queue.get(timeout=5)
            
            if task is TaskQueue.POISON_PILL:
                logger.debug(f"Worker {self.worker_id} received poison pill")
                break
            
            chunk_data: List[str] = task
            self._process_chunk(chunk_data, hasher, logger)
        
        duration = timer.stop()
        logger.log_worker_complete(self.worker_id, duration, self.items_processed)
    
    def _process_chunk(self, chunk: List[str], hasher: Hasher, logger: Logger) -> None:
        """
        Process a chunk of data.
        
        Args:
            chunk: List of strings to hash and compare
            hasher: Hasher instance
            logger: Logger instance
        """
        for item in chunk:
            try:
                computed_hash = hasher.hash(item)
                self.items_processed += 1
                
                if self._compare_hash(computed_hash):
                    self.matches_found += 1
                    self._store_result(item, computed_hash)
                    logger.log_match_found(self.worker_id, item, computed_hash)
                
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error processing '{item}': {e}")
    
    def _compare_hash(self, computed_hash: str) -> bool:
        """
        Compare computed hash with target hash.
        
        Args:
            computed_hash: Hash to compare
        
        Returns:
            True if match, False otherwise
        """
        if not self.target_hash:
            return False
        
        return computed_hash.lower() == self.target_hash
    
    def _store_result(self, original_value: str, hash_value: str) -> None:
        """
        Store match result in shared dictionary.
        
        Args:
            original_value: Original input value
            hash_value: Computed hash
        """
        result_key = f"match_{self.worker_id}_{self.matches_found}"
        
        self.results_dict[result_key] = {
            'worker_id': self.worker_id,
            'original': original_value,
            'hash': hash_value,
            'algorithm': self.algorithm
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get worker statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'worker_id': self.worker_id,
            'items_processed': self.items_processed,
            'matches_found': self.matches_found
        }
