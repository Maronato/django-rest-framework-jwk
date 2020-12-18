from django.urls import path
from .views import JWKList

app_name = "jwk"

urlpatterns = [
    path(".well-known/jwks.json", JWKList.as_view(), name="jwk_list"),
]
