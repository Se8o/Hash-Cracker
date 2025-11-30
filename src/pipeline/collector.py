"""
Parallel Hash Cracking Engine - Collector Module

Author: Sebastian Lodin
Date: November 2025
Description: Collector process for gathering and saving results
"""

from multiprocessing import Process, Manager
from typing import Dict, Any, List
import json
import os
from src.pipeline.logger import Logger
from src.utils.timer import Timer


class Collector(Process):
    """Collector process for gathering and saving results."""
    
    def __init__(self, results_dict: dict, config: Dict[str, Any]):
        super().__init__()
        
        self.results_dict = results_dict
        self.config = config
        self.results_path = config['output']['results_path']
        self.check_interval = config['general'].get('collector_check_interval', 2)
    
    def run(self) -> None:
        """Main collector process loop."""
        logger = Logger.get_instance(
            self.config['output']['log_path'],
            self.config['output']['verbose']
        )
        
        logger.info("Collector started")
        
        self._save_results(logger)
        
        logger.info("Collector finished")
    
    def _save_results(self, logger: Logger) -> None:
        """
        Save results to JSON file.
        
        Args:
            logger: Logger instance
        """
        try:
            os.makedirs(os.path.dirname(self.results_path), exist_ok=True)
            
            results_list = []
            
            for key, value in self.results_dict.items():
                if isinstance(value, dict):
                    results_list.append(value)
            
            output_data = {
                'total_matches': len(results_list),
                'matches': results_list
            }
            
            with open(self.results_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(results_list)} results to {self.results_path}")
        
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    @staticmethod
    def collect_results(results_dict: dict) -> List[Dict[str, Any]]:
        """
        Collect all results from shared dictionary.
        
        Args:
            results_dict: Shared results dictionary
        
        Returns:
            List of result dictionaries sorted by worker_id
        """
        results = []
        
        for key, value in results_dict.items():
            if isinstance(value, dict) and 'original' in value:
                results.append(value)
        
        # Sort results by worker_id for consistent output
        results.sort(key=lambda x: (x.get('worker_id', 0), x.get('original', '')))
        
        return results
    
    @staticmethod
    def print_results(results: List[Dict[str, Any]], logger: Logger) -> None:
        """
        Print results to console.
        
        Args:
            results: List of result dictionaries
            logger: Logger instance
        """
        if not results:
            logger.info("No matches found")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"MATCHES FOUND: {len(results)}")
        logger.info(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            logger.info(f"\nMatch #{i}:")
            logger.info(f"  Worker ID:  {result.get('worker_id', 'N/A')}")
            logger.info(f"  Original:   {result.get('original', 'N/A')}")
            logger.info(f"  Hash:       {result.get('hash', 'N/A')}")
            logger.info(f"  Algorithm:  {result.get('algorithm', 'N/A')}")
        
        logger.info(f"\n{'='*60}")
