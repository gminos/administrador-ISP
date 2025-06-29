from django.urls import path
from base.admin import admin_site

urlpatterns = [
    path("", admin_site.urls),
]
