import threading
import time
import unittest
import logging
from cacheOperations import CacheOperation

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only prints to terminal
    ]
)


class TestCacheSystem(unittest.TestCase):

    def setUp(self):
        # Default cache for most tests
        self.cache = CacheOperation(maxSize=1000, defaultTTL=300)

    def test_basic_operations(self):
        """Test 1: Basic put and get"""
        self.cache.put("config:db_host", "localhost:5432")
        self.cache.put("config:api_key", "abc123", ttl=60)

        self.assertEqual(self.cache.get("config:db_host"), "localhost:5432")
        self.assertEqual(self.cache.get("config:api_key"), "abc123")

    def test_eviction_policy(self):
        """Test 2: Eviction when exceeding maxSize"""
        for i in range(1200):  # Exceeds maxSize of 1000
            self.cache.put(f"data:{i}", f"value_{i}")

        # Check that oldest keys were evicted
        self.assertIsNone(self.cache.get("data:0"))
        self.assertIsNone(self.cache.get("data:199"))
        # Newest items should be retained
        self.assertEqual(self.cache.get("data:1199"), "value_1199")
        self.assertEqual(self.cache.get("data:1000"), "value_1000")

    def test_expiration(self):
        """Test 3: Expiry after TTL"""
        self.cache.put("temp_data", "expires_soon", ttl=2)
        time.sleep(3)  # Wait until expired
        self.assertIsNone(self.cache.get("temp_data"))

    def test_concurrent_access(self):
        """Test 4: Thread-safe concurrent put and get"""
        def worker(thread_id):
            for i in range(100):
                self.cache.put(f"thread_{thread_id}:item_{i}", f"data_{i}")
                self.cache.get(f"thread_{thread_id}:item_{i // 2}")
                time.sleep(0.01)

        threads = []
        for thread_id in range(5):  # 5 concurrent threads
            t = threading.Thread(target=worker, args=(thread_id,), name=f"Worker-{thread_id}")
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Validate some expected values are still present
        self.assertEqual(self.cache.get("thread_0:item_99"), "data_99")
        self.assertEqual(self.cache.get("thread_1:item_50"), "data_50")

    def test_delete_operation(self):
        """Test 5: Delete a specific key"""
        self.cache.put("temp_key", "delete_me")
        self.assertEqual(self.cache.get("temp_key"), "delete_me")
        self.cache.delete("temp_key")
        self.assertIsNone(self.cache.get("temp_key"))

    def test_clear_operation(self):
        """Test 6: Clear the entire cache and reset stats"""
        self.cache.put("key1", "val1")
        self.cache.put("key2", "val2")
        self.cache.put("key3", "val3")
        self.assertEqual(self.cache.get("key1"), "val1")
        self.assertEqual(self.cache.get("key2"), "val2")

        self.cache.clear()

        # All entries should be removed
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNone(self.cache.get("key3"))

        # Stats should be reset
        stats = self.cache.getStats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 3)  # From get after clear
        self.assertEqual(stats["current_size"], 0)
        self.assertEqual(stats["evictions"], 0)  # Not affected by clear
        self.assertEqual(stats["expiredRemovals"], 0)

if __name__ == "__main__":
    unittest.main()
