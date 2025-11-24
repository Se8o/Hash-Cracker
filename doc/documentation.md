# Parallel Hash Cracking Engine - Documentation

## Project Overview

**Parallel Hash Cracking Engine** is a professional cybersecurity tool designed for secure hash verification and lookup using parallel processing. The engine leverages Python's `multiprocessing` module to achieve true parallelism across multiple CPU cores, enabling efficient processing of large datasets.

### Purpose

This tool is designed for legitimate cybersecurity purposes including:
- Password hash verification in penetration testing
- Database integrity validation
- Hash lookup for security audits
- Educational demonstration of parallel computing concepts

## Architecture

### System Components

The project follows a **Producer-Consumer** pattern with the following components:

```
┌──────────────┐
│   Main.py    │
│  (Pipeline)  │
└──────┬───────┘
       │
       ├─────────┐
       │         │
       ▼         ▼
┌──────────┐ ┌───────────┐
│ Receiver │ │  Manager  │
│  (CSV)   │ │  (Shared) │
└────┬─────┘ └─────┬─────┘
     │             │
     ▼             ▼
┌──────────┐ ┌───────────┐
│  Queue   │ │ ResultDict│
└────┬─────┘ └─────▲─────┘
     │             │
     ├─────┬───────┼──────┐
     ▼     ▼       ▼      ▼
  Worker Worker Worker Worker
     │     │       │      │
     └─────┴───────┴──────┘
            │
            ▼
      ┌──────────┐
      │Collector │
      └──────────┘
```

### Class Diagram

```
HashCrackingPipeline
├── ConfigLoader
├── Receiver
├── TaskQueue (Manager.Queue)
├── Worker[] (Process)
│   └── Hasher
├── Collector (Process)
├── Logger (Singleton)
└── Timer

Utils:
├── Chunker
├── Validator
└── Timer
```

## UML Sequence Diagram

```
User -> Pipeline: run()
Pipeline -> ConfigLoader: load()
Pipeline -> Receiver: validate_file()
Pipeline -> Receiver: read_chunks()

loop for each chunk
    Receiver -> TaskQueue: put(chunk)
end

Pipeline -> Worker[]: start()

loop until poison pill
    Worker -> TaskQueue: get()
    Worker -> Hasher: hash(data)
    Worker -> Worker: compare_hash()
    
    alt match found
        Worker -> ResultDict: store_result()
        Worker -> Logger: log_match_found()
    end
end

Pipeline -> TaskQueue: send_poison_pills()
Pipeline -> Worker[]: join()
Pipeline -> Collector: start()
Collector -> ResultDict: collect_results()
Collector -> File: save_results()
Pipeline -> Logger: log_pipeline_stats()
```

## Component Details

### 1. Receiver (Producer)

**Purpose**: Load CSV data and split into chunks

**Key Features**:
- CSV parsing with error handling
- Data validation
- Chunking for parallel distribution
- Statistics tracking

**Methods**:
- `validate_file()` - Check file exists and is readable
- `read_all()` - Load all records
- `read_chunks()` - Iterate through data chunks
- `get_statistics()` - Return processing stats

### 2. TaskQueue (Distribution)

**Purpose**: Thread-safe task distribution using `Manager.Queue`

**Key Features**:
- FIFO task distribution
- Poison pill termination pattern
- Statistics tracking
- Timeout support

**Methods**:
- `put(task)` - Add task to queue
- `get(timeout)` - Retrieve task from queue
- `send_poison_pills(n)` - Send termination signals

### 3. Worker (Consumer)

**Purpose**: Process chunks in parallel using `multiprocessing.Process`

**Key Features**:
- True parallelism (separate processes)
- Hash computation
- Hash comparison
- Result storage in shared memory

**Inheritance**: `Worker(Process)`

**Methods**:
- `run()` - Main worker loop
- `_process_chunk()` - Process data chunk
- `_compare_hash()` - Compare with target
- `_store_result()` - Save to shared dict

### 4. Hasher

**Purpose**: Compute cryptographic hashes

**Supported Algorithms**:
- **SHA256** - 256-bit secure hash
- **SHA384** - 384-bit secure hash
- **SHA512** - 512-bit secure hash
- **PBKDF2-HMAC-SHA256** - Password-based key derivation

**Methods**:
- `hash(data, salt)` - Compute hash
- `verify(data, hash)` - Verify hash match
- `quick_hash(data, algorithm)` - Static quick hash

### 5. Collector

**Purpose**: Gather results from workers and save to file

**Key Features**:
- Collects from `Manager.dict()`
- JSON output format
- Result statistics
- Console output

**Methods**:
- `collect_results()` - Gather all matches
- `print_results()` - Display to console
- `_save_results()` - Save to JSON file

### 6. Logger

**Purpose**: Thread-safe logging with Lock

**Key Features**:
- Singleton pattern
- Multiprocessing-safe (Lock)
- File and console output
- Multiple log levels

**Synchronization**: Uses `multiprocessing.Lock`

**Methods**:
- `info()`, `debug()`, `warning()`, `error()`
- `log_worker_start()`, `log_worker_complete()`
- `log_match_found()`
- `log_pipeline_stats()`

## Synchronization Mechanisms

### 1. Lock

Used in **Logger** for thread-safe writes:

```python
with self.write_lock:
    self.logger.info(message)
```

### 2. Semaphore

Used in **Pipeline** to limit concurrent workers:

```python
self.semaphore = Semaphore(max_workers)
```

### 3. Manager.Queue

Producer-Consumer communication:

```python
self.queue = Manager().Queue()
```

### 4. Manager.dict

Shared results storage:

```python
self.results_dict = Manager().dict()
```

## Worker Pool Architecture

### Pool Management

- Configurable worker count (config: `worker_count`)
- Maximum worker limit (config: `max_workers`)
- Semaphore-based concurrency control
- Graceful shutdown with poison pills

### Work Distribution

```python
chunks = Chunker.chunk_list(data, chunk_size)
for chunk in chunks:
    task_queue.put(chunk)
```

### Process Lifecycle

1. **Creation**: `Worker(worker_id, queue, results, config)`
2. **Start**: `worker.start()` (spawns new process)
3. **Execution**: `worker.run()` (main loop)
4. **Termination**: Poison pill → `worker.join()`

## Configuration

### config.json Structure

```json
{
  "general": {
    "worker_count": 4,        // Number of worker processes
    "chunk_size": 10000,      // Items per chunk
    "max_workers": 8,         // Maximum concurrent workers
    "timeout_seconds": 300    // Worker timeout
  },
  "hash": {
    "algorithm": "SHA256",    // Hash algorithm
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
    "hash_to_find": ""        // Target hash to search for
  }
}
```

### Algorithm Selection

- **SHA256**: Fast, 64 hex characters
- **SHA384**: Medium, 96 hex characters
- **SHA512**: Strong, 128 hex characters
- **PBKDF2**: Secure password hashing (salted)

## Error Handling

### File Errors

- **FileNotFoundError**: CSV file missing
- **PermissionError**: No read access
- **UnicodeDecodeError**: Encoding issues

### Configuration Errors

- **Invalid worker_count**: Must be ≥ 1
- **Invalid chunk_size**: Must be ≥ 1
- **Invalid algorithm**: Must be in supported list
- **Invalid hash format**: Length and hex validation

### Runtime Errors

- **Worker timeout**: Configurable timeout
- **Keyboard interrupt**: Graceful cleanup
- **Process termination**: Resource cleanup

## Testing

### Test Files

1. **test_hasher.py**: Hash computation tests
   - SHA256/384/512 correctness
   - PBKDF2 functionality
   - Verification tests
   - Edge cases

2. **test_pipeline.py**: Pipeline integration tests
   - Receiver data loading
   - Chunking logic
   - Queue operations
   - Result collection

3. **test_config.py**: Configuration tests
   - Valid config loading
   - Validation rules
   - Get/Set operations
   - Error handling

### Running Tests

```bash
python -m unittest discover test
python -m unittest test.test_hasher
python -m unittest test.test_pipeline
python -m unittest test.test_config
```

## Performance Considerations

### Chunking Strategy

- Smaller chunks: Better load balancing, more overhead
- Larger chunks: Less overhead, potential imbalance
- Recommended: 1,000 - 10,000 items per chunk

### Worker Count

- **CPU-bound**: Set to CPU core count
- **Too many workers**: Context switching overhead
- **Too few workers**: Underutilized resources

### Memory Usage

- **Manager.dict()**: Shared memory overhead
- **Queue size**: Limited by available memory
- **CSV loading**: Loads entire file into memory

## Security Considerations

### Ethical Use

This tool is designed for:
- ✓ Authorized penetration testing
- ✓ Security audits with permission
- ✓ Educational purposes
- ✓ Database integrity verification

NOT for:
- ✗ Unauthorized access attempts
- ✗ Illegal password cracking
- ✗ Privacy violations

### Hash Security

- **SHA256/384/512**: NOT salted by default
- **PBKDF2**: Properly salted and iterated
- **Rainbow tables**: SHA hashes vulnerable
- **Best practice**: Use PBKDF2 for passwords

## Use Case Scenarios

### Scenario 1: Birth Number Verification

```csv
# data/birth_numbers.csv
9001011234
8512251234
7503031234
```

**Config**:
- Algorithm: SHA256
- Target: Hash of specific birth number
- Workers: 4

**Result**: Find which birth number matches hash

### Scenario 2: Password Database Audit

```csv
# data/passwords.csv
password123
admin
letmein
```

**Config**:
- Algorithm: PBKDF2
- Target: Stored PBKDF2 hash
- Workers: 8

**Result**: Identify weak passwords

## Troubleshooting

### Issue: Workers hang

**Solution**: Check timeout settings, ensure poison pills sent

### Issue: No matches found

**Solution**: Verify target hash format, check algorithm match

### Issue: Memory error

**Solution**: Reduce chunk_size, process CSV in batches

### Issue: Permission denied

**Solution**: Check file permissions, create output directories

## Future Enhancements

- Distributed processing across machines
- GPU acceleration for hash computation
- Real-time progress reporting
- Database input/output support
- Additional hash algorithms (bcrypt, scrypt)
- Resume capability for large datasets

## Conclusion

This Parallel Hash Cracking Engine demonstrates professional implementation of:

1. **True Parallelism**: multiprocessing.Process
2. **Producer-Consumer Pattern**: Queue-based task distribution
3. **Shared Memory**: Manager.dict() and Manager.Queue()
4. **Synchronization**: Lock and Semaphore
5. **Chunking**: Efficient data distribution
6. **Error Handling**: Comprehensive error management
7. **Testing**: Unit tests for all components
8. **Documentation**: Complete technical documentation

The architecture is scalable, maintainable, and follows Python best practices for parallel computing in cybersecurity applications.
