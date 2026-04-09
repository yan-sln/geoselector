# -*- coding: utf-8 -*-
"""TTL-aware LRU cache decorator for GeoSelector.

Provides a decorator that wraps functools.lru_cache with time-based expiration.
"""

import time
import threading
from functools import lru_cache, wraps
from typing import Any, Callable, TypeVar, Dict, Tuple

T = TypeVar("T")


def ttl_lru_cache(maxsize: int = 128, ttl: int = 300):
    """LRU cache with time-to-live expiration.

    This decorator combines LRU caching with time-based expiration. Entries are
    evicted based on both recency (LRU) and age (TTL). The cache keeps at most
    `maxsize` entries, and entries older than `ttl` seconds are removed.

    Parameters
    ----------
    maxsize : int, optional
        Maximum number of cached entries (default: 128)
    ttl : int, optional
        Time-to-live in seconds for cached entries (default: 300)

    Returns
    -------
    callable
        Decorator function that applies the TTL-aware LRU cache
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create a thread-safe LRU cache
        cached_func = lru_cache(maxsize=maxsize)(func)
        cache_data: Dict[Tuple, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        cache_lock = threading.Lock()

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Create a hashable key from arguments
            key = _make_key(args, kwargs)

            with cache_lock:
                # Check if cache entry exists and is still valid
                if key in cache_data:
                    value, timestamp = cache_data[key]
                    if time.time() - timestamp < ttl:
                        # Cache hit - update timestamp
                        cache_data[key] = (value, time.time())
                        # Return cached result by calling the original function with the same args
                        return cached_func(*args, **kwargs)
                    else:
                        # Cache expired - remove entry
                        del cache_data[key]

            # Cache miss - call original function
            result = func(*args, **kwargs)

            # Store result in cache and timestamp
            with cache_lock:
                cache_data[key] = (result, time.time())

            return result

        # Expose cache clearing functionality
        def cache_clear():
            cached_func.cache_clear()
            with cache_lock:
                cache_data.clear()

        # Assign cache_clear to the wrapper function
        setattr(wrapper, "cache_clear", cache_clear)

        return wrapper

    return decorator


def _make_key(args: tuple, kwargs: dict) -> tuple:
    """Create a hashable cache key from function arguments.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Hashable tuple representing the arguments
    """
    # Convert kwargs to a sorted tuple of items to ensure consistent ordering
    kwargs_tuple = tuple(sorted(kwargs.items()))
    return (args, kwargs_tuple)
