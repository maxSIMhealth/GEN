from rest_framework import routers

from django.urls import include, path

app_name = "api"

# Registering API routes
router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("", include(router.urls)),
]
