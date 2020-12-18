from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from django.core.cache import BaseCache
from django.utils.module_loading import import_string
from .settings import api_settings
from .utils import aware_utcnow


GET_CACHE_CALLBACK = api_settings.GET_CACHE_CALLBACK

get_cache: Callable[[], BaseCache] = (
    GET_CACHE_CALLBACK
    if callable(GET_CACHE_CALLBACK)
    else import_string(GET_CACHE_CALLBACK)
)


JWKS_CACHE_PREFIX = api_settings.CACHE_PREFIX
JWKS_CACHE_LIST = f"{JWKS_CACHE_PREFIX}:jwk_list"
JWKS_CACHE_EXPIRES = f"{JWKS_CACHE_PREFIX}:jwk_expires"


should_cache: bool = api_settings.CACHE_JWK_RESPONSES


def dump_jwks_into_cache(jwks: List[Dict[str, Any]], expires: datetime):
    if should_cache:
        cache = get_cache()
        timeout = round((expires - aware_utcnow()).total_seconds())
        cache.set(key=JWKS_CACHE_LIST, value=jwks, timeout=timeout)
        cache.set(key=JWKS_CACHE_EXPIRES, value=expires, timeout=timeout)


def load_jwks_from_cache() -> Tuple[Optional[List[Dict[str, Any]]], Optional[datetime]]:
    if should_cache:
        cache = get_cache()
        jwks = cache.get(key=JWKS_CACHE_LIST, default=None)
        expires = cache.get(key=JWKS_CACHE_EXPIRES, default=None)
        return jwks, expires
    else:
        return None, None


def clear_jwks_cache():
    if should_cache:
        cache = get_cache()
        cache.delete(key=JWKS_CACHE_LIST)
        cache.delete(key=JWKS_CACHE_EXPIRES)
