import json
from typing import Any, Mapping, Optional, Type, Union, cast
from datetime import datetime
from uuid import uuid4, UUID
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.dispatch import receiver
from django.conf import settings

from jwcrypto import jwk, jwt, jws

from . import algorithms
from .exceptions import UnsupportedAlgorithmError, JWKExpired
from .utils import aware_utcnow
from .settings import api_settings
from .cache import clear_jwks_cache


class JWK(models.Model):
    created_at: datetime = models.DateTimeField(_("Created at"), editable=False)
    expires_at: datetime = models.DateTimeField(
        _("Expires at"), null=True, editable=False
    )
    rotated_at: Optional[datetime] = models.DateTimeField(
        _("Rotated at"), null=True, editable=False
    )

    KEY_ALGORITHMS = tuple(map(lambda x: (x, x), algorithms.ALLOWED_ALGORITHMS))
    algorithm: str = models.CharField(
        _("Algorithm"),
        max_length=10,
        choices=KEY_ALGORITHMS,
        blank=True,
        default=algorithms.KEY_ALGORITHM_RS512,
    )

    private_key_pem: bytes = models.BinaryField(
        _("Private key"), null=True, default=None, editable=False
    )
    key_uuid: UUID = models.UUIDField(_("Key ID"), editable=False, default=uuid4)

    # EdDSA variables
    EdDSA_CURVES = tuple(map(lambda x: (x, x), algorithms.ALLOWED_EdDSA_CURVES))
    eddsa_curve: str = models.CharField(
        _("EdDSA curve"),
        max_length=10,
        choices=EdDSA_CURVES,
        blank=True,
        default=algorithms.EdDSA_CURVE_Ed25519,
    )

    # RSA variables
    rsa_public_exponent: int = models.IntegerField(
        _("RSA public exponent"), default=algorithms.DEFAULT_RSA_EXPONENT
    )
    RSA_SIZES = tuple(map(lambda x: (x, str(x)), algorithms.ALLOWED_RSA_SIZES))
    rsa_size: int = models.IntegerField(
        _("RSA key size"), choices=RSA_SIZES, default=algorithms.RSA_SIZE_2048
    )

    @property
    def key_type(self):
        if self.algorithm in algorithms.RSA_ALGORITHMS:
            return algorithms.KEY_TYPE_RSA
        elif self.algorithm in algorithms.EC_ALGORITHMS:
            return algorithms.KEY_TYPE_ELLIPTIC_CURVE
        elif self.algorithm in algorithms.EdDSA_ALGORITHMS:
            return algorithms.KEY_TYPE_EDWARDS_CURVE
        return None

    @property
    def curve(self):
        if self.key_type == algorithms.KEY_TYPE_ELLIPTIC_CURVE:
            return algorithms.EC_CURVE_MAP[self.algorithm]
        elif self.key_type == algorithms.KEY_TYPE_EDWARDS_CURVE:
            return self.eddsa_curve
        return None

    @property
    def key_id(self) -> str:
        return str(self.key_uuid)

    def get_password(self) -> bytes:
        return settings.SECRET_KEY.encode()

    def generate_private_key(self) -> "JWK":
        key_type = self.key_type
        if key_type == algorithms.KEY_TYPE_RSA:
            private_key = jwk.JWK.generate(
                kty="RSA", public_exponent=self.rsa_public_exponent, size=self.rsa_size
            )
        elif key_type == algorithms.KEY_TYPE_ELLIPTIC_CURVE:
            private_key = jwk.JWK.generate(kty="EC", crv=self.curve)
        elif key_type == algorithms.KEY_TYPE_EDWARDS_CURVE:
            private_key = jwk.JWK.generate(kty="OKP", crv=self.curve)
        else:
            raise UnsupportedAlgorithmError(self.algorithm)

        private_key._params["kid"] = self.key_id

        self.private_key_pem = private_key.export_to_pem(
            True, password=self.get_password()
        )
        self.save()
        return self

    def export(self):
        return self.public_key.export_public(True)

    @property
    def private_key(self):
        priv = jwk.JWK.from_pem(self.private_key_pem, password=self.get_password())
        priv._params["kid"] = self.key_id
        priv._params["alg"] = self.algorithm
        return priv

    @property
    def public_key(self):
        return self.private_key.public()

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return aware_utcnow() > self.expires_at

    @property
    def is_rotated(self) -> bool:
        if self.rotated_at is not None:
            return True
        return aware_utcnow() > self.created_at + api_settings.JWK_LIFETIME

    @classmethod
    def get_current_jwk(cls) -> "JWK":
        current = cast(Optional["JWK"], cls.objects.first())
        if current is None or current.is_rotated:
            current = cls.rotate_keys()

        return current

    @classmethod
    def rotate_keys(cls) -> "JWK":
        previous_jwk = cast(Optional["JWK"], cls.objects.first())
        current_time = aware_utcnow()
        expires_at = None
        if api_settings.JWK_EXPIRE_TIME:
            expires_at = (
                current_time + api_settings.JWK_LIFETIME + api_settings.JWK_EXPIRE_TIME
            )
        instance: JWK = cls(
            algorithm=api_settings.ALGORITHM,
            rsa_size=api_settings.RSA_KEY_SIZE,
            rsa_public_exponent=api_settings.RSA_PUBLIC_EXPONENT,
            eddsa_curve=api_settings.EdDSA_CURVE,
            created_at=current_time,
            expires_at=expires_at,
        )

        if previous_jwk is not None:
            previous_jwk.rotated_at = current_time
            previous_jwk.save()

        return instance.generate_private_key()

    @classmethod
    def encode(
        cls,
        claims: Mapping[str, Any],
        headers: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Encode a JWT

        Uses the latest valid JWK to encode your claims.

        Args:
            claims (Mapping[str, Any]): Payload to encode.
            headers (Optional[Mapping[str, Any]], optional): Extra headers. Defaults to None.

        Returns:
            str: Encoded JWT
        """
        current_key = cls.get_current_jwk()

        header = headers.copy() if headers is not None else {}
        header["typ"] = "JWT"
        header["alg"] = current_key.algorithm
        header["kid"] = current_key.key_id

        if current_key.algorithm in algorithms.EdDSA_ALGORITHMS:
            header["crv"] = current_key.curve

        token = jwt.JWT(header=header, claims=claims, **kwargs)
        token.make_signed_token(current_key.private_key)

        return token.serialize()

    @classmethod
    def decode(cls, data: Union[str, bytes], **kwargs) -> Mapping[str, Any]:
        """Decode a JWT

        Attempts to use the JWK declared by the "kid" header parameter and falls back to the
        current JWK if not available.

        Throws if the provided JWT is not valid or if the requested key ID is expired.

        Args:
            data (Union[str, bytes]): Encoded JWT to be decoded.

        Returns:
            Mapping[str, Any]: JWT claims (payload).
        """
        sig = jws.JWS()
        sig.deserialize(data)
        key_id = sig.jose_header.get("kid")
        key = None
        if key_id is not None:
            key = cast(Optional["JWK"], cls.objects.filter(key_uuid=key_id).first())
        if key is None:
            key = cls.get_current_jwk()

        if key.is_expired:
            raise JWKExpired(key.key_id)

        token = jwt.JWT(jwt=data, key=key.public_key, **kwargs)
        return json.loads(token.claims)

    def __str__(self):
        return f"JWK #{self.key_id} ({self.algorithm})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("JWK")
        verbose_name_plural = _("JWKs")


@receiver(models.signals.pre_save, sender=JWK)
def generate_jwk_keys(sender: Type[JWK], instance: JWK, **kwargs):
    # If being created
    if instance.id is None and instance.private_key is None:
        instance.generate_private_key()

    # Clear cache
    clear_jwks_cache()
