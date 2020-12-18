from django.core.management.base import BaseCommand

from ...models import JWK


class Command(BaseCommand):
    help = "Rotates the JWK"

    def handle(self, *args, **kwargs):
        JWK.rotate_keys()
