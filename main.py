import functools
import sys
from collections import OrderedDict, Counter
from typing import Any, TypeAlias, Callable

import requests

CACHED_DICT: TypeAlias = dict[str, Any]
DECORATOR_FUNCTION: TypeAlias = Callable[[], None]


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


def memory_monitoring(some_function: Callable) -> DECORATOR_FUNCTION:
    def get_size_function(*args):
        print(sys.getsizeof(some_function(args)))

    return get_size_function


def fetch_url(url, first_n=100):
    """Fetch a given url"""
    res = requests.get(url)
    return res.content[:first_n] if first_n else res.content


link = "https://docs.python.org/3/library/venv.html"

@memory_monitoring
@cache(max_limit=100)
def catch_cache(result_of_request: int | bytes) -> CACHED_DICT:
    return Counter(result_of_request)


print(catch_cache(fetch_url(link)))
