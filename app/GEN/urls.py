"""GEN URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core import views as core_views
from rest_framework.authtoken import views as authtoken_views

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView, TemplateView
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(
        r"^favicon.ico$",
        RedirectView.as_view(
            url=staticfiles_storage.url("favicon.ico"), permanent=False
        ),
        name="favicon",
    ),
]

# tiny mce
urlpatterns += [
    path("tinymce/", include("tinymce.urls")),
]

# rest framework api
urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
    path("api-token-auth/", authtoken_views.obtain_auth_token, name="api-token-auth"),
    path("api/", include("api.urls", namespace="api")),
]

# GEN apps
urlpatterns += i18n_patterns(
    path("", include("dashboard.urls")),
    path("", include("accounts.urls")),
    path("", include("courses.urls")),
    path("", include("core.urls")),
    path("", include("videos.urls")),
    path("", include("quiz.urls")),
    path("", include("discussions.urls")),
    path("", include("scorm.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    prefix_default_language=False
    # admin
    # path("admin/", admin.site.urls),
)

urlpatterns += i18n_patterns(path("admin/", admin.site.urls))

urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
)

if settings.DEBUG:
    # enable rosetta
    if "rosetta" in settings.INSTALLED_APPS:
        urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]

    # access to media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # delete user data
    urlpatterns += (path("reset/", core_views.reset, name="reset"),)

    # django toolbar
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
