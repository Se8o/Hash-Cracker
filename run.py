#!/usr/bin/env python3
"""
Parallel Hash Cracking Engine
Quick start script with example configuration
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    print("=" * 60)
    print("PARALLEL HASH CRACKING ENGINE - Quick Start")
    print("=" * 60)
    print()
    print("This will run the engine with default configuration.")
    print("To find 'test' in data/sample_data.csv")
    print()
    
    # Override sys.argv to use default config
    sys.argv = ['run.py', 'config.json']
    
    main()
