import time

MAX_CACHE_SIZE = 20  # максимальна кількість записів у кеші

class Cache:
    def __init__(self, ttl):
        self.storage = {}
        self.ttl = ttl  # час життя кешу в секундах

    def get(self, key):
        if key in self.storage:
            value, timestamp, custom_ttl = self.storage[key]
            ttl = custom_ttl if custom_ttl is not None else self.ttl
            if key == "last_chat_id" or (time.time() - timestamp < ttl):
                return value
            else:
                # Видаляємо протерміновані записи одразу при зверненні
                del self.storage[key]
        return None

    def set(self, key, value, ttl=None):
        self._evict_expired()

        # Якщо кеш переповнений — видаляємо найстаріший запис
        if len(self.storage) >= MAX_CACHE_SIZE and key not in self.storage:
            oldest_key = min(
                self.storage,
                key=lambda k: self.storage[k][1]
            )
            del self.storage[oldest_key]

        self.storage[key] = (value, time.time(), ttl)

    def _evict_expired(self):
        now = time.time()
        expired = []
        for k, (_, ts, custom_ttl) in self.storage.items():
            if k == "last_chat_id":
                continue
            ttl = custom_ttl if custom_ttl is not None else self.ttl
            if now - ts >= ttl:
                expired.append(k)
        for k in expired:
            del self.storage[k]

    def delete(self, key):
        self.storage.pop(key, None)

    def clear(self):
        self.storage.clear()

    def size(self):
        return len(self.storage)