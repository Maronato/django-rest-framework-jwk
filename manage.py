import sys
import django
from django.conf import settings

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.messages",
    "rest_framework_jwk",
]

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    USE_I18N=True,
    SECRET_KEY="abc123",
    DATABASES={
        "default": {
            "NAME": "db.sqlite3",
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    MIDDLEWARE=(
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
    ),
    SITE_ID=1,
    INSTALLED_APPS=INSTALLED_APPS,
    ROOT_URLCONF="tests.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "context_processors": [
                    # Default template context processors:
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        }
    ],
    SIMPLE_JWT={"ALGORITHM": "RS512"},
)

django.setup()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
