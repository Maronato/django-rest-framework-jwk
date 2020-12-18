from django.utils.translation import gettext_lazy as _
from jwcrypto.common import JWException


class UnsupportedAlgorithmError(Exception):
    def __init__(self, algorithm: str):
        message = _('Unrecognized algorithm type "{algorithm}".').format(
            algorithm=algorithm
        )

        super().__init__(message)


class UnsupportedCurveError(Exception):
    def __init__(self, curve: str):
        message = _('Unrecognized curve type "{curve}".').format(curve=curve)

        super().__init__(message)


class JWKExpired(JWException):
    """JWK Expired Exception

    This exception is raised when an expired JWK is used.
    """

    def __init__(self, kid: str) -> None:
        message = _('The JSON Web Key with Key ID "{kid}" has expired.').format(kid=kid)
        super().__init__(message)
