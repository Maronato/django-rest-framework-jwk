# djangorestframework-jwk

## Overview

Easy JSON Web Keys (JWK) for your Django project.

In particular, this implements [RFC 7517](https://tools.ietf.org/html/rfc7517), [] [RFC 7518](https://tools.ietf.org/html/rfc7518), and [RFC 8037](https://tools.ietf.org/html/rfc8037), which allows you to create and maintain a rotating, public [JWK set](https://tools.ietf.org/html/rfc7517#section-5) and use it to issue and validate JWTs signed with any of the following algorithms:

- RSA:
  - RS256
  - RS384
  - RS512
  - PS256
  - PS384
  - PS512
- Elliptic-Curve (EC)
  - ES256
  - ES384
  - ES512
- Octet (OKP)
  - EdDSA with Ed25519
  - EdDSA with Ed448


## Requirements

-  Python (3.6, 3.7, 3.8, 3.9)
-  Django (2.2, 3.0, 3.1)
-  Django REST Framework (3.10, 3.11, 3.12)


## Installation

Install it from the repo:
```
pip install git+https://github.com/maronato/django-rest-framework-jwk.git
```

Add `rest_framework_jwk` to your installed apps:
```py
INSTALLED_APPS = (
    ...
    'rest_framework_jwk',
)
```

Sync your database:
```
python manage.py migrate rest_framework_jwk
```

That's it!

## Usage

You can now encode and decode JWTs using:
```py
>>> from rest_framework_jwk.jwt import encode, decode

>>> claims = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
}

>>> token = encode(claims) # Encoded JWT string

>>> print(token)
eyJhbGciOiJSUzUxMiIsImtpZCI6IjAyZTAwNjI2LTQ4ZTEtNDQ3Yy1iMGJkLWUwMTI5ZWEzODkyNyIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1MTYyMzkwMjIsIm5hbWUiOiJKb2huIERvZSIsInN1YiI6IjEyMzQ1Njc4OTAifQ.k10xfTyPuJj8VXjAxt93dXWI8bSPgiJ9qT5712QsU3X2BdT8NwG0PKnKuiC-xIoy6kcn2PumbWituHTPCbuo70vmKQYJ12pdfhfVGrPoorVF-8dRm8JL-BwLcpg_ZHaiMbeialeJAyXz_4sL2LHDbQX1LEVzLqACTnoCY62BjHX14w8YBaF55smZaDu4ltRKvgVjaxytqeYYG-AGNGZfWyAZshsF28Lh-QYZFUOqKS5pF_SYSvjtgTk2Uh1n9DeazGBcbG7EeCMjoxTvALBdcBt4cGB7rREqKSSzNcVPMPA91Odmxav49n1LElRknXSd_noqlF6xMWOFaX5h-9KzgQ

>>> decode(token) # Validates and returns the token claims
{'iat': 1516239022, 'name': 'John Doe', 'sub': '1234567890'}
```

## Making the JWK set public
If your users need to access the public component of your keys for validation, add `rest_framework_jwk.urls` to your `urls.py`:
```py

urlpatterns = [
    ...

    path(r"", include('rest_framework_jwk.urls', namespace='rest_framework_jwk')),
]
```

Now navigate to [http://localhost:8000/.well-known/jwks.json](http://localhost:8000/.well-known/jwks.json) and you'll see the public components of every JWK generated, with the most recent at the top.

## Settings

All configurations are namespaced under the `JWK` settings.

For example:
```py
JWK = {
    "ALGORITHM": "RS512",
    "RSA_KEY_SIZE": 2048,
}
```

| Setting               | Default                                        | Type                  | Description                                                                                                                                                                                                                                                               |
| --------------------- | ---------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ALGORITHM`           | `"RS512"`                                      | `str`                 | The algorithm used to generate JWKs and sign JWTs. The list of choices is defined below.                                                                                                                                                                                  |
| `JWK_LIFETIME`        | `timedelta(days=7)`                            | `timedelta`           | A [timedelta](https://docs.python.org/3/library/datetime.html) representing how long a JWK should be used before being rotated.                                                                                                                                           |
| `JWK_EXPIRE_TIME`     | `timedelta(days=7)`                            | `timedelta | None`    | A [timedelta](https://docs.python.org/3/library/datetime.html) (or `None`) representing how long a JWK can be used to validate JWTs **after** it's rotated. If set to `None`, JWKs are never expired. Usually this should be the same value as the lifetime of your JWTs. |
| `CACHE_JWK_RESPONSES` | `True`                                         | `bool`                | Whether or not the responses given by the JWK set public endpoint should be cached.                                                                                                                                                                                       |
| `CACHE_PREFIX`        | `"rest_framework_jwk"`                         | `str`                 | The cache key prefix.                                                                                                                                                                                                                                                     |
| `GET_CACHE_CALLBACK`  | `"rest_framework_jwk.utils.get_default_cache"` | `str | callable`      | A callable or the import string of a callable that returns a Django cache instance to be used. Defaults to the `default` Django cache.                                                                                                                                    |
| `RSA_KEY_SIZE`        | `2048`                                         | `1024 | 2048 | 4096`  | The size of the generated RSA keys.                                                                                                                                                                                                                                       |
| `RSA_PUBLIC_EXPONENT` | `65537`                                        | `int`                 | The public exponent to be used by the RSA algorithm. You should leave it at `65537` unless you have a really good reason.                                                                                                                                                 |
| `EdDSA_CURVE`         | `"Ed25519"`                                    | `"Ed25519" | "Ed448"` | The EdDSA curve to be used.                                                                                                                                                                                                                                               |

### Available algorithms
The list of available algorithms to use is the following:

- `"RS256"`
- `"RS384"`
- `"RS512"`
- `"PS256"`
- `"PS384"`
- `"PS512"`
- `"ES256"`
- `"ES384"`
- `"ES512"`
- `"EdDSA"`
