"""Utilities

Some functions were taken from
https://github.com/SimpleJWT/django-rest-framework-simplejwt/blob/master/rest_framework_simplejwt/utils.py
"""

from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.utils.timezone import is_naive, make_aware, utc
from django.core.cache import caches, BaseCache


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)

    return dt


def aware_utcnow():
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return make_utc(datetime.utcfromtimestamp(ts))


def get_default_cache() -> BaseCache:
    return caches["default"]
