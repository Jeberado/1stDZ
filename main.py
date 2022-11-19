import functools
import os
from collections import OrderedDict, Counter
from typing import Any, TypeAlias, Callable

import psutil
import requests as requests

CACHED_DICT: TypeAlias = dict[str, Any]
DECORATOR_FUNCTION: TypeAlias = Callable[[], None]


def record_memory_usage(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info()[0]
        rt = func(*args, **kwargs)
        mem_end = process.memory_info()[0]
        diff_kb = (mem_end - mem_start) // 1000
        print(f'memory usage of {func.__name__}: {diff_kb} KB')
        return rt

    return wrapper


def cache(max_limit=64):
    def internal(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            cache_key = (args, tuple(kwargs.items()))
            if cache_key in deco._cache:
                # переносимо в кінець списку
                deco._cache.move_to_end(cache_key, last=True)
                return deco._cache[cache_key]
            result = f(*args, **kwargs)
            # видаляємо якшо досягли ліміта
            if len(deco._cache) >= max_limit:
                # видаляємо перший елемент
                deco._cache.popitem(last=False)
            deco._cache[cache_key] = result
            return result

        deco._cache = OrderedDict()
        return deco

    return internal


@record_memory_usage
@cache(max_limit=100)
def fetch_url(url, first_n=100):
    """Fetch a given url"""
    res = requests.get(url)
    return res.content[:first_n] if first_n else res.content


link = "https://pavel-karateev.gitbook.io/intermediate-python/dekoratory/function_caching"


def catch_cache(result_of_request: int | bytes) -> CACHED_DICT:
    return Counter(result_of_request)


print(catch_cache(fetch_url(link)))
