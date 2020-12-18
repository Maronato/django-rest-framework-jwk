from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JWKConfig(AppConfig):
    name = "rest_framework_jwk"
    verbose_name = _("JWK")
