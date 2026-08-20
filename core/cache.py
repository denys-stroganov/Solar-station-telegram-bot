import time
from datetime import date

MAX_CACHE_SIZE = 100  # максимальна кількість записів у кеші

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

    # ----------------------------------------------------
    # ХЕЛПЕРИ КЕШУВАННЯ СТАТИСТИКИ З РОЗДІЛЕНИМ TTL
    # ----------------------------------------------------
    def get_or_fetch_year_stats(self, client, year_param=None):
        today_year = date.today().year

        if year_param:
            req_year = int(year_param)
            cache_key = f"year_column_data_{req_year}"
            is_past = req_year < today_year
        else:
            cache_key = "year_column_data"
            is_past = False

        cached = self.get(cache_key)
        if cached:
            return cached

        data = client.get_year_column_info(year=year_param)
        ttl = 2592000 if is_past else 86400  # 30 днів для минулих років, 24г для поточного
        self.set(cache_key, data, ttl=ttl)
        return data

    def get_or_fetch_month_stats(self, client, year_param=None, month_param=None):
        today = date.today()

        if year_param and month_param:
            req_year = int(year_param)
            req_month = int(month_param)
            cache_key = f"month_column_data_{req_year}_{req_month}"
            is_past = (req_year < today.year) or (req_year == today.year and req_month < today.month)
        else:
            cache_key = "month_column_data"
            is_past = False

        cached = self.get(cache_key)
        if cached:
            return cached

        data = client.get_month_column_info(year=year_param, month=month_param)
        ttl = 2592000 if is_past else 3600  # 30 днів для минулих місяців, 1г для поточного
        self.set(cache_key, data, ttl=ttl)
        return data

    def get_or_fetch_day_multiline(self, client, date_text: str):
        cache_key = f"day_multiline_{date_text}"
        
        cached = self.get(cache_key)
        if cached:
            return cached
            
        data = client.get_day_multiline_info(date_text)
        
        today_str = date.today().strftime("%Y-%m-%d")
        is_past = date_text < today_str
        ttl = 2592000 if is_past else 600  # 30 days for past, 10 minutes for current day
        self.set(cache_key, data, ttl=ttl)
        return data