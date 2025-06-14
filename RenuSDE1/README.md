# Thread Safe In Memory Cache System (Python)

This project is a custom **in-memory caching system** implemented in Python that supports:

- **Thread safety** using locks
- **Time To Live (TTL)** support for cache entries
- **LRU (Least Recently Used)** eviction policy
- **Background cleanup thread** for expired keys
- **Real-time statistics tracking**

---

## How to Run the code

1. **Clone the repository**
  `git clone https://github.com/Prasadrenu/Thread-safe-in-memory-cache-system`
  or  Download zip files from the repository
2. **Navigate to directory**
   `cd cacheSystem`
3. **To run the code**
     Use command ` python -m unittest -v tests.TestCacheSystem`
## Dependencies

This project uses only standard Python libraries and requires **no external packages** for core functionality.

However, for testing and debugging purposes, the following libraries are used:

- `unittest` – For writing and running test cases.
- `threading` – To support concurrent operations in the cache.
- `logging` – To enable debug level logging and help trace operations.
- `time` – For managing TTL (time to live) expiry logic.

> All dependencies are part of the Python Standard Library. So no additional installation via `pip` is required.


## Design Decisions

This cache system was built with simplicity, performance, and thread safety in mind. Key design choices include:

- **In Memory Storage:** All data is stored using HashMap/Dictionary (`cacheMap` and `expiryMap`) to ensure fast O(1) access and mutation.
  
- **TTL Handling:** Each cache entry can have an optional Time To Live (TTL). A background thread periodically checks and removes expired keys which acts as a background cleanup worker.

- **LRU Eviction Policy:** When the cache size exceeds the defined `maxSize`, the Least Recently Used (LRU) item is evicted. This is managed by the `LRUEviction` class, which is implemented using a doubly linked list to allow efficient O(1) insertions, deletions, and updates of access order.

- **Statistics Tracking:** The cache tracks hits, misses, evictions, current size, total request, hitrate and expired removals in real time to provide operational visibility.

- **Modular Structure:** The code is modular with well separated concerns  eviction, cleanup, stats, and core operations are implemented in isolation for maintainability.

- **Logging:** Logging is used to trace flow and debug multithreaded access, helping in both development and production monitoring.

### Concurrency Model

This cache system is designed to be thread safe, allowing concurrent access from multiple threads without data corruption or race conditions.

- **`threading.Lock`** is used to ensure that only one thread can modify the shared cache structures (`cacheMap`, `expiryMap`, stats, etc.) at a time.
- The lock is acquired in all key operations (`put`, `get`, `delete`, `clear`) to protect shared state and maintain consistency.
- A **background cleanup thread** (`_cleanupExpiredKeys`) runs as a daemon to continuously monitor and remove expired keys without blocking the main execution threads. It will automatically terminate when the program exits.

Using this locking mechanism and separation of background tasks ensures high reliability in multi threaded environments like web servers or background jobs.

### Eviction Logic

The cache uses an **LRU (Least Recently Used)** eviction policy to manage memory efficiently when the number of entries exceeds the configured `maxSize`.

- An internal **`LRUEviction`** class is implemented using a **Doubly Linked List** and a **Hash Map** to ensure O(1) time complexity for insertions, deletions, and lookups.
- Each time a key is accessed or inserted, it is moved to the most recently used position (head position of doubly linked list).
- When the cache exceeds its maximum size:
  - The **least recently used** key (i.e., the tail of the doubly linked list) is evicted.
  - The key is removed from both `cacheMap` and `expiryMap`, and the `evictions` stat is incremented.

This design ensures the cache retains frequently accessed items and evicts stale or rarely used data efficiently.


### Sample Stats Output

The in memory cache system tracks various statistics in real time, including:

- `hits`:  2   
- `misses`:  2 
- `hit_rate`:  0.5 
- `current_size`:  3
- `evictions`:   0
- `totalRequests`:  4 
- `expiredRemovals`:   0
> All the sample console outputs including stats, are placed inside the OutputFiles folder

### Performance Considerations

- **In-Memory Speed**: Since the entire cache resides in memory, access and update operations (`get`, `put`, `delete`) are extremely fast typically O(1) time complexity using internal dictionaries.

- **TTL Management**: The use of a dedicated **background thread** ensures that expired keys are cleaned up automatically without delaying main thread operations. This thread runs continuously and checks expiration every second.

- **Thread Safety**: Python’s `threading.Lock` is used during critical read/write/delete operations to prevent race conditions during concurrent access by multiple threads.

- **LRU Efficiency**: The LRU eviction policy is implemented using a **doubly linked list** and hashmap for efficient O(1) eviction and updates, ensuring scalability when handling large data volumes.

- **Scalability**: The system is optimized for high read/write throughput and performs well under concurrent workloads, as demonstrated in the unit tests with multiple threads writing simultaneously.

> For best performance, ensure `maxSize` is chosen based on available memory and workload patterns.


