"""
Parallel Hash Cracking Engine - Receiver Module

Author: Sebastian Lodin
Date: November 2025
Description: CSV data receiver and chunking engine
"""

import csv
import os
from typing import List, Dict, Any, Iterator
from src.utils.chunker import Chunker
from src.utils.validator import Validator
from src.pipeline.logger import Logger


class Receiver:
    """CSV data receiver and chunking engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.csv_path = config['input']['csv_path']
        self.encoding = config['input'].get('csv_encoding', 'utf-8')
        self.delimiter = config['input'].get('csv_delimiter', ',')
        self.chunk_size = config['general']['chunk_size']
        self.logger = Logger.get_instance()
        
        self.total_lines = 0
        self.valid_lines = 0
        self.invalid_lines = 0
    
    def validate_file(self) -> bool:
        """
        Validate that CSV file exists and is readable.
        
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(self.csv_path):
            self.logger.error(f"CSV file not found: {self.csv_path}")
            return False
        
        if not os.path.isfile(self.csv_path):
            self.logger.error(f"Path is not a file: {self.csv_path}")
            return False
        
        if not os.access(self.csv_path, os.R_OK):
            self.logger.error(f"No read permission for file: {self.csv_path}")
            return False
        
        return True
    
    def count_lines(self) -> int:
        """
        Count total lines in CSV file.
        
        Returns:
            Number of lines
        """
        try:
            with open(self.csv_path, 'r', encoding=self.encoding) as f:
                return sum(1 for _ in f)
        except Exception as e:
            self.logger.error(f"Error counting lines: {e}")
            return 0
    
    def read_all(self) -> List[str]:
        """
        Read all valid records from CSV.
        
        Returns:
            List of record strings
        """
        records = []
        
        try:
            with open(self.csv_path, 'r', encoding=self.encoding) as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                
                for line_num, row in enumerate(reader, 1):
                    self.total_lines += 1
                    
                    # Skip empty rows
                    if not row or len(row) == 0:
                        self.invalid_lines += 1
                        self.logger.debug(f"Empty row at line {line_num}")
                        continue
                    
                    # Get first column and strip whitespace
                    record = row[0].strip()
                    
                    # Skip empty or whitespace-only records
                    if not record:
                        self.invalid_lines += 1
                        self.logger.debug(f"Empty record at line {line_num}")
                        continue
                    
                    records.append(record)
                    self.valid_lines += 1
            
            self.logger.info(f"Loaded {self.valid_lines} valid records from {self.csv_path}")
            
            if self.invalid_lines > 0:
                self.logger.warning(f"Skipped {self.invalid_lines} invalid lines")
            
            return records
        
        except FileNotFoundError:
            self.logger.error(f"File not found: {self.csv_path}")
            return []
        except PermissionError:
            self.logger.error(f"Permission denied: {self.csv_path}")
            return []
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error reading CSV: {e}. Try different encoding.")
            return []
        except Exception as e:
            self.logger.error(f"Error reading CSV: {e}")
            return []
    
    def read_chunks(self) -> Iterator[List[str]]:
        """
        Read CSV in chunks for memory efficiency.
        
        Yields:
            Chunks of records
        """
        records = self.read_all()
        
        if not records:
            return
        
        for chunk in Chunker.chunk_list(records, self.chunk_size):
            yield chunk
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get receiver statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_lines': self.total_lines,
            'valid_lines': self.valid_lines,
            'invalid_lines': self.invalid_lines
        }
