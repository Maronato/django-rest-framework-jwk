from django.contrib import admin

from .models import JWK


@admin.register(JWK)
class JWKAdmin(admin.ModelAdmin):
    list_display = (
        "algorithm",
        "key_id",
        "expires_at",
        "created_at",
    )
    search_fields = (
        "key_id",
        "algorithm",
    )
