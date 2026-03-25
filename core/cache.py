import time

class Cache:
    def __init__(self, ttl):
        self.storage = {}
        self.ttl = ttl # час життя кешу в секундах

    def get(self, key):
        if key in self.storage:
            value, timestamp = self.storage[key]
            if key == "last_chat_id" or (time.time() - timestamp < self.ttl):
                return value
        return None

    def set(self, key, value):
        self.storage[key] = (value, time.time())