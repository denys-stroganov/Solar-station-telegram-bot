import redis
import os
import logging
import time

r = redis.from_url(os.getenv("REDIS_URL"))

_subscribers_cache = []
_last_loaded = 0
CACHE_TTL = 300  # refresh every 5 minutes

def load_subscribers() -> list[int]:
    global _subscribers_cache, _last_loaded

    if time.time() - _last_loaded > CACHE_TTL:
        try:
            members = r.smembers("subscribers")
            _subscribers_cache = [int(m) for m in members]
            _last_loaded = time.time()
            logging.info(f"[Subscribers] Refreshed: {_subscribers_cache}")
        except Exception as e:
            logging.error(f"[Subscribers] Failed to load: {e}")

    return _subscribers_cache

def save_subscriber(chat_id: int):
    try:
        r.sadd("subscribers", chat_id)
        _subscribers_cache.append(chat_id)
        logging.info(f"[Subscribers] Saved subscriber: {chat_id}")
    except Exception as e:
        logging.error(f"[Subscribers] Failed to save {chat_id}: {e}")