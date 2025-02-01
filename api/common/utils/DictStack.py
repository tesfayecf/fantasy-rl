class DictStack:
    def __init__(self, size):
        self.size = size
        self.stack = {}
        self.keys = []

    def push(self, key, value):
        if key in self.stack:
            self.stack[key] = value
        elif len(self.keys) >= self.size:
            oldest_key = self.keys.pop(0)
            del self.stack[oldest_key]
            self.stack[key] = value
            self.keys.append(key)
        else:
            self.stack[key] = value
            self.keys.append(key)

    def pop(self):
        if self.keys:
            key = self.keys.pop()
            value = self.stack.pop(key)
            return key, value
        else:
            return None

    def delete(self, key):
        if key in self.stack:
            self.keys.remove(key)
            del self.stack[key]
        else:
            raise KeyError(f"Key '{key}' not found in the stack.")

    def get(self, key):
        """Get an element by key, return False if it does not exist."""
        if key in self.stack:
            return self.stack[key]
        else:
            return False

    def is_empty(self):
        """Check if the stack is empty."""
        return not bool(self.keys)

    def size(self):
        """Return the size of the stack."""
        return len(self.keys)

    def peek(self):
        """Get the top element without removing it from the stack."""
        if self.is_empty():
            return None
        key = self.keys[-1]
        value = self.stack[key]
        return (key, value)

    def clear(self):
        """Clear the stack."""
        self.stack = {}
        self.keys = []

    def get_elements(self):
        """Return all elements in the stack as a list of (key, value) tuples."""
        return [(key, self.stack[key]) for key in self.keys]
