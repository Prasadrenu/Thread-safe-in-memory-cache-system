class LRUEviction:
    """
    A doubly linked list to perform LRU Eviction.
    Supports O(1) access,update,delete and move operations.
    
    """
    def __init__(self):
        self.head=None
        self.tail=None

    def addToFront(self,node):
        """
        Insert most recently used operation at the begining.
        
        """
        node.previous=None 
        node.next=self.head 

        if self.head:       # If already node is present make the node connect to tail of present node
            self.head.previous=node
        self.head=node      # To make sure node is front

        if self.tail is None:
            self.tail=node

    def removeNode(self,node):
        """
        Remove a node from anywhere in the linked list.

        """
        if not node:
            return None
        if node.previous:           # If previous node is present just remove connection
            node.previous.next=node.next
        else:
            self.head=node.next     # As it is first node we just move head
        
        if node.next:           # If it is not tail remove connection
            node.next.previous=node.previous
        else:
            self.tail=node.previous # As it is the tail we move tail to previous one

        node.previous=None
        node.next=None

    def moveToFront(self,node):
        """
        Access order should be updated to front in list on every get and put operation
        
        """
        if node is None:
            return None
        self.removeNode(node)   # First we remove the node
        self.addToFront(node)   # We add it at front
        
    def removeLeastRecentlyUsed(self):
        """
        Remove and return the least recently used node(tail node). 
        
        """
        if self.tail:   # If thers is Tail we remove and return it
            removeNode=self.tail
            self.removeNode(removeNode)
            return removeNode
        return None