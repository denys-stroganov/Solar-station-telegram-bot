async def get_or_cache(cache, key, fetch_function):
    cached = cache.get(key)
    if cached:
        return cached

    data = await fetch_function()
    cache.set(key, data)
    return data