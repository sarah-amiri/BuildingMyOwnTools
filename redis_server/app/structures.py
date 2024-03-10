class Node:
    def __init__(self, value):
        self._value = str(value)
        self._next = None

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = str(val)

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, val):
        self._next = val


class LinkedList:
    def __init__(self):
        self._head = None
        self._tail = None
        self._length = 0

    def __len__(self):
        return self._length

    @property
    def head(self):
        return self._head

    @property
    def tail(self):
        return self._tail

    def insert_first(self, *values):
        first_node = node = Node(values[0])
        for value in values[1:]:
            new_node = Node(value)
            new_node.next = first_node
            first_node = new_node

        if self._head is None and self._tail is None:
            self._head, self._tail = first_node, node
        else:
            node.next = self._head
            self._head = first_node
        self._length += len(values)

    def insert_last(self, *values):
        first_node = node = Node(values[0])
        for value in values[1:]:
            new_node = Node(value)
            first_node.next = new_node
            first_node = new_node

        if self._head is None and self._tail is None:
            self._head, self._tail = node, first_node
        else:
            self._tail.next = node
            self._tail = node
        self._length += len(values)

    def traverse(self, start, stop):
        index = 0
        node = self._head
        while index < start and node:
            node = node.next
            index += 1

        result = []
        if node is None:
            return result

        if stop < 0:
            stop = len(self) + stop
        stop += 1
        while index < stop and node:
            result.append(node.value)
            node = node.next
            index += 1
        return result
