class _Item:
    """Lightweight composite to store key-value pairs."""
    __slots__ = '_key', '_value'

    def __init__(self, k, v):
        self._key = k
        self._value = v

    def __lt__(self, other):
        return self._key < other._key  # Compare items based on their keys

    def __str__(self):
        return f"({self._key}, '{self._value}')"

    def __repr__(self):
        return str(self)

class HeapPriorityQueue:
    """A min-oriented priority queue implemented with a binary heap."""

    #------------------------------ nonpublic behaviors ------------------------------
    def _parent(self, j):
        return (j - 1) // 2

    def _left(self, j):
        return 2 * j + 1

    def _right(self, j):
        return 2 * j + 2

    def _has_left(self, j):
        return self._left(j) < len(self._data)

    def _has_right(self, j):
        return self._right(j) < len(self._data)

    def _swap(self, i, j):
        """Swap the elements at indices i and j of array."""
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _upheap(self, j):
        parent = self._parent(j)
        if j > 0 and self._data[j] < self._data[parent]:
            self._swap(j, parent)
            self._upheap(parent) # recur at new position of item

    def _downheap(self, j):
        if self._has_left(j):
            left = self._left(j)
            small_child = left          # assume left child is smallest
            if self._has_right(j):
                right = self._right(j)
                if self._data[right] < self._data[left]:
                    small_child = right
            if self._data[small_child] < self._data[j]:
                self._swap(j, small_child)
                self._downheap(small_child) # recur at new position of parent

    #------------------------------ public behaviors ------------------------------
    def __init__(self):
        """Create a new empty Priority Queue."""
        self._data = []

    def __len__(self):
        """Return the number of items in the priority queue."""
        return len(self._data)

    def is_empty(self):
        """Return True if the priority queue is empty."""
        return len(self) == 0

    def add(self, key, value):
        """Add a key-value pair to the priority queue."""
        self._data.append(_Item(key, value))
        self._upheap(len(self._data) - 1)

    def min(self):
        """Return but do not remove (key,value) pair with minimum key.

        Raise Exception if empty.
        """
        if self.is_empty():
            raise Exception("Priority queue is empty")
        item = self._data[0]
        return (item._key, item._value)

    def remove_min(self):
        """Remove and return (key,value) pair with minimum key.

        Raise Exception if empty.
        """
        if self.is_empty():
            raise Exception("Priority queue is empty")
        self._swap(0, len(self._data) - 1)  # put minimum item at the end
        item = self._data.pop()             # remove it from the list
        self._downheap(0)                   # restore heap property
        return (item._key, item._value)
    
# Membuat objek priority queue
pq = HeapPriorityQueue()

# Data sesuai tree (assuming this represents the tree from your image/PPT)
data = [
    (4,'C'),
        (5,'A'), (6,'Z'),
            (15,'K'), (9,'F'), (7,'Q'), (20,'B'),
                (16,'X'), (25,'J'), (14,'E'), (12,'H'), (11,'S'), (13,'W')
                ]

# Insert ke heap
for key, value in data:
    pq.add(key, value)

# Tampilkan isi heap setelah semua elemen ditambahkan
print("Heap array after all additions:")
for item in pq._data:
    print(item)

# Ambil elemen minimum (root)
if not pq.is_empty():
    print("\nMinimum:", pq.min())
else:
    print("\nHeap is empty, cannot get minimum.")

# Hapus minimum
if not pq.is_empty():
    print("Remove min:", pq.remove_min())
else:
    print("Heap is empty, cannot remove minimum.")

# Heap setelah penghapusan
print("\nHeap setelah remove_min:")
if not pq.is_empty():
    for item in pq._data:
        print(item)
else:
    print("Heap is empty.")