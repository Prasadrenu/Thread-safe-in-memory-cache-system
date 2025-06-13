class Cache:
    """
    Creating a node to use in the double linked list( for LRU Eviction).
    Each node stores a key, value, expirationTime, and pointers to move
    start to end vice versa.

    """

    def __init__(self,key,value=None):
        """
        A doubly linked list
        
        """
        self.key=key
        self.value=value
        self.previous=None
        self.next=None