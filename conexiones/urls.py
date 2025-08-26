from django.urls import path
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from base.admin import admin_site

urlpatterns = [
    path("", admin_site.urls),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico', permanent=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
