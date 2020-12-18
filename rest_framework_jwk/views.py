from datetime import datetime
from typing import List
from django.db.models.query import QuerySet
from django.utils.http import http_date
from rest_framework import permissions, views, request, response
from .models import JWK
from .utils import datetime_to_epoch, aware_utcnow
from .cache import dump_jwks_into_cache, load_jwks_from_cache


def make_response(keys: List, expires_at: datetime) -> response.Response:
    expires = http_date(datetime_to_epoch(expires_at))
    max_age = max(round((expires_at - aware_utcnow()).total_seconds()), 0)
    return response.Response(
        {"keys": keys},
        headers={
            "Expires": expires,
            "Cache-Control": f"max-age={max_age}, must-revalidate",
        },
    )


class JWKList(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: request.Request):
        cached_keys, cached_expires = load_jwks_from_cache()
        if cached_keys is not None and cached_expires is not None:
            return make_response(cached_keys, cached_expires)

        current_jwk = JWK.get_current_jwk()
        jwks: QuerySet[JWK] = JWK.objects.all()
        keys = list(map(lambda k: k.export(), jwks))

        expires = current_jwk.expires_at
        dump_jwks_into_cache(keys, expires)

        return make_response(keys, expires)
