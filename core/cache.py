import time

MAX_CACHE_SIZE = 20  # максимальна кількість записів у кеші

class Cache:
    def __init__(self, ttl):
        self.storage = {}
        self.ttl = ttl  # час життя кешу в секундах

    def get(self, key):
        if key in self.storage:
            value, timestamp = self.storage[key]
            if key == "last_chat_id" or (time.time() - timestamp < self.ttl):
                return value
            else:
                # Видаляємо протерміновані записи одразу при зверненні
                del self.storage[key]
        return None

    def set(self, key, value):
        self._evict_expired()

        # Якщо кеш переповнений — видаляємо найстаріший запис
        if len(self.storage) >= MAX_CACHE_SIZE and key not in self.storage:
            oldest_key = min(
                self.storage,
                key=lambda k: self.storage[k][1]
            )
            del self.storage[oldest_key]

        self.storage[key] = (value, time.time())

    def _evict_expired(self):
        now = time.time()
        expired = [
            k for k, (_, ts) in self.storage.items()
            if k != "last_chat_id" and now - ts >= self.ttl
        ]
        for k in expired:
            del self.storage[k]

    def delete(self, key):
        self.storage.pop(key, None)

    def clear(self):
        self.storage.clear()

    def size(self):
        return len(self.storage)