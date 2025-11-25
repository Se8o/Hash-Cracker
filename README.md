# Parallel Hash Cracking Engine

Professional cybersecurity tool for secure hash verification and lookup using parallel processing with Python's multiprocessing.

## Project Description

This engine leverages **true parallelism** through `multiprocessing.Process` to efficiently process large datasets and compare cryptographic hashes across multiple CPU cores. Designed for legitimate cybersecurity purposes including penetration testing, security audits, and educational demonstrations.

### Key Features

- **True Parallelism**: Uses `multiprocessing`, not threading or asyncio
- **Multiple Hash Algorithms**: SHA256, SHA384, SHA512, PBKDF2-HMAC
- **Producer-Consumer Pattern**: Queue-based task distribution
- **Shared Memory**: `Manager.dict()` and `Manager.Queue()`
- **Synchronization**: Lock and Semaphore mechanisms
- **Chunking**: Efficient data distribution to workers
- **Thread-Safe Logging**: Multiprocessing-safe logger with Lock
- **Comprehensive Testing**: Unit tests for all components
- **Standard Library Only**: No heavy dependencies

## Requirements

- Python 3.7 or higher
- Standard library only (no external dependencies)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Se8o/Hasher.git
cd Hasher
```

2. No additional dependencies to install - uses Python standard library only!

3. Quick test run:
```bash
python run.py
```

## Project Structure

```
Hasher/
├── src/
│   ├── main.py                    # Main pipeline orchestrator
│   ├── config_loader.py           # Configuration management
│   ├── pipeline/
│   │   ├── receiver.py            # CSV data loader and chunker
│   │   ├── task_queue.py          # Task distribution queue
│   │   ├── worker.py              # Parallel worker processes
│   │   ├── collector.py           # Result collector
│   │   ├── hasher.py              # Hash computation engine
│   │   └── logger.py              # Thread-safe logger
│   └── utils/
│       ├── timer.py               # Execution timer
│       ├── chunker.py             # Data chunking utilities
│       └── validator.py           # Validation functions
├── test/
│   ├── test_hasher.py             # Hash engine tests
│   ├── test_pipeline.py           # Pipeline integration tests
│   └── test_config.py             # Configuration tests
├── doc/
│   └── documentation.md           # Complete technical documentation
├── data/                          # Input CSV files
├── logs/                          # Log and result files
└── config.json                    # Configuration file
```

## Configuration

Edit `config.json` to configure the engine:

```json
{
  "general": {
    "worker_count": 4,
    "chunk_size": 10000,
    "max_workers": 8,
    "timeout_seconds": 300
  },
  "hash": {
    "algorithm": "SHA256",
    "pbkdf2_iterations": 100000,
    "pbkdf2_salt_length": 32
  },
  "input": {
    "csv_path": "data/sample_data.csv",
    "csv_encoding": "utf-8",
    "csv_delimiter": ","
  },
  "output": {
    "log_path": "logs/hasher.log",
    "results_path": "logs/results.json",
    "verbose": true
  },
  "target": {
    "hash_to_find": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  }
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `worker_count` | Number of parallel worker processes | 4 |
| `chunk_size` | Number of items per chunk | 10000 |
| `algorithm` | Hash algorithm (SHA256/SHA384/SHA512/PBKDF2) | SHA256 |
| `csv_path` | Path to input CSV file | data/sample_data.csv |
| `hash_to_find` | Target hash to search for | "" |

## Usage

### Web UI (Easiest)

1. Start web server:
```bash
python web_server.py
```

2. Open browser at `http://localhost:8080`

3. Enter data and hash, click "Start Search"

### Command Line Usage

1. Create a CSV file with data to hash (e.g., `data/sample_data.csv`):
```csv
test1
test2
test3
password
admin
user123
```

2. Configure the target hash in `config.json`:
```json
{
  "target": {
    "hash_to_find": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  }
}
```

3. Run the engine:
```bash
python src/main.py
```

### Custom Configuration

```bash
python src/main.py custom_config.json
```

### Example Output

```
============================================================
PARALLEL HASH CRACKING ENGINE
============================================================
INFO - Validating pipeline setup...
INFO - Validation passed
INFO - Creating 4 worker processes...
INFO - Started 4 workers
INFO - Loaded 10 chunks into queue
INFO - Worker 0 started processing waiting for tasks
INFO - Worker 1 started processing waiting for tasks
INFO - Worker 2 FOUND MATCH: test -> 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
INFO - Worker 2 completed: 2500 items in 1.23s

============================================================
MATCHES FOUND: 1
============================================================

Match #1:
  Worker ID:  2
  Original:   test
  Hash:       9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
  Algorithm:  SHA256

============================================================
INFO - Pipeline completed in 2.45s
INFO - Total items processed: 10000
INFO - Matches found: 1
INFO - Processing rate: 4081.63 items/sec
============================================================
```

## Example CSV Files

### Birth Numbers
```csv
# data/birth_numbers.csv
9001011234
8512251234
7503031234
9510155678
```

### Passwords
```csv
# data/passwords.csv
password
123456
admin
letmein
qwerty
```

### Generic Data
```csv
# data/sample_data.csv
test
hello
world
data123
```

## Running Tests

Run all tests:
```bash
python -m unittest discover test
```

Run specific test file:
```bash
python -m unittest test.test_hasher
python -m unittest test.test_pipeline
python -m unittest test.test_config
```

## Hash Algorithms

### SHA256 (Default)
- **Length**: 64 hex characters
- **Use case**: General purpose, fast
- **Example**: `9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08`

### SHA384
- **Length**: 96 hex characters
- **Use case**: Enhanced security
- **Example**: `768412320f7b0aa5812fce428dc4706b3cae50e02a64caa16a782249bfe8efc4b7ef1ccb126255d196047dfedf17a0a9`

### SHA512
- **Length**: 128 hex characters
- **Use case**: Maximum security
- **Example**: `ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff`

### PBKDF2-HMAC-SHA256
- **Length**: Variable (salt + key)
- **Use case**: Password hashing (salted & iterated)
- **Iterations**: Configurable (default: 100,000)

## Educational Value

This project demonstrates:

1. **Multiprocessing Concepts**
   - `multiprocessing.Process` for true parallelism
   - `Manager.Queue()` for task distribution
   - `Manager.dict()` for shared memory
   - Process synchronization

2. **Parallel Patterns**
   - Producer-Consumer pattern
   - Worker pool architecture
   - Poison pill termination

3. **Synchronization Mechanisms**
   - `Lock` for thread-safe logging
   - `Semaphore` for worker limiting
   - Shared memory management

4. **Software Engineering**
   - Clean architecture
   - Comprehensive testing
   - Error handling
   - Professional documentation

## Security & Ethics

### Legitimate Uses
✅ Authorized penetration testing  
✅ Security audits with permission  
✅ Educational purposes  
✅ Database integrity verification  

### Prohibited Uses
❌ Unauthorized access attempts  
❌ Illegal password cracking  
❌ Privacy violations  

**Use responsibly and only on systems you own or have explicit permission to test.**

## Performance Tips

### Optimal Worker Count
- Set to number of CPU cores for CPU-bound tasks
- Check available cores: `python -c "import os; print(os.cpu_count())"`

### Chunk Size
- **Small chunks (100-1,000)**: Better load balancing, more overhead
- **Large chunks (10,000-100,000)**: Less overhead, potential imbalance
- **Recommended**: 1,000-10,000 for most use cases

### Memory Considerations
- Entire CSV is loaded into memory
- For very large files, consider implementing streaming

## Troubleshooting

### Workers hang or timeout
- Check `timeout_seconds` in config
- Verify poison pills are sent correctly
- Review worker logs

### No matches found
- Verify target hash format (correct length, hex characters)
- Ensure algorithm matches hash type
- Check case sensitivity (normalized to lowercase)

### Permission denied
- Ensure read access to input CSV
- Ensure write access to logs directory
- Create output directories if missing

### Memory errors
- Reduce `chunk_size`
- Reduce `worker_count`
- Process file in batches

## Documentation

Complete technical documentation available in:
- [doc/documentation.md](doc/documentation.md) - Architecture, UML diagrams, component details

## Contributing

This is an educational project. For improvements:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

Educational project - use responsibly and ethically.

## Author

Built as a demonstration of parallel computing concepts in Python for cybersecurity applications.

## 🔗 Related Concepts

- Multiprocessing vs Threading vs Asyncio
- Producer-Consumer pattern
- Hash functions in cryptography
- Parallel computing in Python
- Process synchronization
- Cybersecurity tools development

---

**Note**: This tool is designed for educational and authorized security testing purposes only. Always obtain proper authorization before testing any systems.
