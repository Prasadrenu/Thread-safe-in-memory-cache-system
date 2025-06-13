import time,threading,logging
from LRUEviction import LRUEviction
from cacheCreation import Cache

class CacheOperation:
    """
    Our main class which stores all the operatoins to be done on cache

    """
    def __init__(self, maxSize, defaultTTL):
        # Using hashmap for fast lookups
        self.cacheMap={}                  # To store key, value pairs
        self.expiryMap={}                      # To store key, expiry time
        self.LRUEviction=LRUEviction()
        self.defaultTTL=defaultTTL       # To store defaultTTL if it is not given while creating an item
        self.maxSize=maxSize    # Maximum size of the cache, if it exceeds remove least recenltly used Item
        self.lock=threading.Lock()      # To support concurrent get and put operations from multiple threads
        self.stats={
            "hits":0,   # If the item is found
            "misses":0, # If the item is not found
            "hit_rate":0.0, # total hits/totalrequests
            "current_size":0,   # size of cache at present
            "evictions":0,  # Number of times an item is used due to maximum memory limit reached
            "totalRequests":0,  # sum of hits and misses
            "expiredRemovals":0 # number of items expired
        }
        # To removes expired entries, daemon=True below, says it's a background thread and automatically terminates when program exists, it won't block the programme
        self.cleanupThread=threading.Thread(target=self._cleanupExpiredKeys, daemon=True) 
        self.cleanupThread.start()

    def put(self,key,value,ttl=None):
        """
            put method is to add new item if it is not already present
            else update the value of the item and move item to top in
            LRUEviction list
                
        """
        self.currentTime=time.time()
        self.lock.acquire()        # Apply lock to perform operation without allowin for race condition
        if key in self.cacheMap:    # If the item alreay present update value and move item to top
            node=self.cacheMap[key]
            node.value=value
            self.LRUEviction.moveToFront(node)
        else:
            # Create new item and insert into the front of the LRUEviction list
            try:
                if key is None or type(key)!=str:
                    raise ValueError("Invalid key: Key must be a string with a value")
            except Exception as e:
                logging.debug(e)
            node=Cache(key,value)
            self.LRUEviction.addToFront(node)
            self.cacheMap[key]=node
        # To support both default TTL and pre-entry TTL
        if ttl is not None:
            self.expiryTime=self.currentTime+ttl
        else:
                self.expiryTime=self.currentTime+self.defaultTTL
        self.expiryMap[key]=self.expiryTime
        # When the number of entries exceeds max_size, evict the least recently used item
        if len(self.cacheMap)>self.maxSize:
            logging.debug("Maximum cache memory exceeded")
            lruNode=self.LRUEviction.removeLeastRecentlyUsed()
            if lruNode:
                del self.cacheMap[lruNode.key]
                del self.expiryMap[lruNode.key]
                self.stats["evictions"]+=1
        self.lock.release()     # To overcome situations like deadlock release the lock suc that another process uses it

    def _removeKey(self,key):
        """
        To remove the key from cacheMap and expiryMap and also from LRUEviction list
        
        """
        if key in self.cacheMap:
            node=self.cacheMap[key]
            if node is not None:
                self.LRUEviction.removeNode(node)
            del self.cacheMap[key]

        if key in self.expiryMap:
            del self.expiryMap[key]

    def get(self,key):
        """
        To return the value of item if the item is present else
        return None
        
        """
        self.lock.acquire()
        if key not in self.cacheMap:
            self.stats["misses"]+=1
            self.stats["totalRequests"]+=1
            self.lock.release()
            return None
        # Check if expired
        expiry=self.expiryMap[key]
        if expiry is not None and time.time()>=self.expiryMap[key]:
            logging.debug(f"key {key} - has expired")
            self._removeKey(key)
            self.stats["expiredRemovals"]+=1
            self.stats["misses"]+=1
            self.stats["totalRequests"]+=1
            self.lock.release()
            return None
        # If it is a valid hit move node to front in list and return value
        node=self.cacheMap[key]
        self.LRUEviction.moveToFront(node)
        self.stats["hits"]+=1
        self.stats["totalRequests"]+=1
        self.lock.release()
        if node:
            return node.value 
        else:
                return None       
    def delete(self,key):
        """
        Deletes the key if it exists else return None
        
        """
        self.lock.acquire()
        if key in self.cacheMap:
            self._removeKey(key)
        else:  
            logging.debug(f'Key {key} not found')
        self.lock.release()

    def clear(self):
        """
        clears all the hashmap and sets all values to 0 in stats
        
        """
        self.lock.acquire()
        self.cacheMap.clear()
        self.expiryMap.clear()
        self.LRUEviction=LRUEviction()
        self.stats={
        "hits":0,
        "misses":0,
        "hit_rate":0.0,
        "current_size":0,
        "evictions":0,
        "totalRequests":0,
        "expiredRemovals":0
    }
        self.lock.release()
            
    def getStats(self):
        """
        return the stats at present
        
        """
        if self.stats["totalRequests"]>0:   
            self.stats["hitRate"]=self.stats["hits"]/self.stats["totalRequests"] # formula to calculate totalRequests
        else:
            self.stats["hitRate"]=0.0
        self.stats["current_size"]=len(self.cacheMap)
        return self.stats
    
    def _cleanupExpiredKeys(self):
        """
        Acts as a background cleanup worker to periodically remove expired items
        
        """
        while True:  # To run until main program end
            keysToDelete=[]
            currentTime=time.time()
            for key,expiryTime in self.expiryMap.items():
                if expiryTime and expiryTime<=currentTime:
                    keysToDelete.append(key)

            for key in keysToDelete:
                try:
                    self._removeKey(key)
                    logging.debug(f'Key {key}- has expired')
                except Exception as e:
                    logging.debug(f'cleanup thread error removing key {key}',{e})
                self.stats["expiredRemovals"]+=1
            
            time.sleep(1) # we have to efficienlty check expired keys for every second in background