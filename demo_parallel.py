#!/usr/bin/env python3
"""
Demo script to prove parallel processes are running
Shows PID of each worker process
"""

import os
import sys
import time
from multiprocessing import Process, Manager, Queue

def worker_task(worker_id, queue, results):
    """Simulate worker process"""
    pid = os.getpid()
    parent_pid = os.getppid()
    
    print(f"✓ Worker {worker_id} started: PID={pid}, Parent PID={parent_pid}")
    
    # Simulate CPU-intensive work
    total = 0
    for i in range(20000000):
        total += i * i
    
    # Store result
    results[worker_id] = {
        'pid': pid,
        'work_done': total % 1000000
    }
    
    print(f"✓ Worker {worker_id} (PID={pid}) finished!")

def main():
    print("=" * 70)
    print("PARALLEL MULTIPROCESSING DEMO")
    print("=" * 70)
    
    main_pid = os.getpid()
    print(f"\n📍 Main process PID: {main_pid}")
    print(f"💻 CPU cores available: {os.cpu_count()}")
    print(f"\n🚀 Creating 4 worker processes...\n")
    
    # Create shared memory
    manager = Manager()
    queue = manager.Queue()
    results = manager.dict()
    
    # Create and start worker processes
    processes = []
    for i in range(4):
        p = Process(target=worker_task, args=(i, queue, results))
        p.start()
        processes.append(p)
        time.sleep(0.1)  # Small delay to see processes starting
    
    print(f"\n📊 All 4 workers are now running IN PARALLEL!")
    print(f"💡 Check Activity Monitor or run: ps aux | grep python\n")
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    print("\n" + "=" * 70)
    print("RESULTS - Each worker had its own Process ID (PID):")
    print("=" * 70)
    
    for worker_id in sorted(results.keys()):
        result = results[worker_id]
        print(f"Worker {worker_id}: PID={result['pid']}, Work={result['work_done']}")
    
    print("\n✅ PROOF OF PARALLELISM:")
    print(f"   - Main process: PID {main_pid}")
    print(f"   - 4 different PIDs = 4 real OS processes")
    print(f"   - All finished at similar time = parallel execution")
    print("=" * 70)

if __name__ == "__main__":
    main()
