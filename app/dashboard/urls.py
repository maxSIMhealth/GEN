from dashboard import views as dashboard_views

from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", dashboard_views.dashboard, name="home"),
    path("dashboard/", RedirectView.as_view(url="/"), name="dashboard"),
]
