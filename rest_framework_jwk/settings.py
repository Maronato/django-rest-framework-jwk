from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings as _APISettings
from .algorithms import (
    RSA_SIZE_2048,
    KEY_ALGORITHM_RS512,
    EdDSA_CURVE_Ed25519,
    DEFAULT_RSA_EXPONENT,
    ALLOWED_ALGORITHMS,
    ALLOWED_RSA_SIZES,
    ALLOWED_EdDSA_CURVES,
)

USER_SETTINGS = getattr(settings, "JWK", None)

DEFAULTS = {
    # Base options
    "ALGORITHM": KEY_ALGORITHM_RS512,
    "JWK_LIFETIME": timedelta(days=7),
    "JWK_EXPIRE_TIME": timedelta(days=7),  # Or None
    "CACHE_JWK_RESPONSES": True,
    "CACHE_PREFIX": "rest_framework_jwk",
    "GET_CACHE_CALLBACK": "rest_framework_jwk.utils.get_default_cache",
    # RSA options
    "RSA_KEY_SIZE": RSA_SIZE_2048,
    "RSA_PUBLIC_EXPONENT": DEFAULT_RSA_EXPONENT,
    # EdDSA options
    "EdDSA_CURVE": EdDSA_CURVE_Ed25519,
}

IMPORT_STRINGS = ()


class APISettings(_APISettings):  # pragma: no cover
    def __check_user_settings(self, user_settings):
        docs = "https://github.com/Maronato/django-rest-framework-jw#settings"

        if user_settings.ALGORITHM not in ALLOWED_ALGORITHMS:
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The algorithm "{algorithm}" is not supported. Please refer to "{docs}" for a list of available algorithms.'
                ).format(algorithm=user_settings.ALGORITHM, docs=docs)
            )

        if user_settings.RSA_KEY_SIZE not in ALLOWED_RSA_SIZES:
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The RSA key size "{key_size}" is not supported. Please refer to "{docs}" for a list of available key sizes.'
                ).format(key_size=user_settings.RSA_KEY_SIZE, docs=docs)
            )

        if user_settings.EdDSA_CURVE not in ALLOWED_EdDSA_CURVES:
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The EdDSA curve "{curve}" is not supported. Please refer to "{docs}" for a list of available curves.'
                ).format(curve=user_settings.EdDSA_CURVE, docs=docs)
            )

        if not isinstance(user_settings.RSA_PUBLIC_EXPONENT, int):
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The RSA public exponent ("RSA_PUBLIC_EXPONENT") must be an integer value. Instead it was "{type}"'
                ).format(type=type(user_settings.RSA_PUBLIC_EXPONENT))
            )

        if not isinstance(user_settings.JWK_LIFETIME, timedelta):
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The JWK lifetime ("JWK_LIFETIME") must be a timedelta instance. Instead it was "{type}"'
                ).format(type=type(user_settings.JWK_LIFETIME))
            )

        if (
            not isinstance(user_settings.JWK_EXPIRE_TIME, timedelta)
            and user_settings.JWK_EXPIRE_TIME is not None
        ):
            raise RuntimeError(
                _(
                    '[rest_framework_jwk] The JWK expire time ("JWK_EXPIRE_TIME") must be a timedelta instance or None. Instead it was "{type}"'
                ).format(type=type(user_settings.JWK_LIFETIME))
            )

        return user_settings


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "JWK":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
