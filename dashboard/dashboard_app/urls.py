from django.contrib import admin
from django.urls import include, path
from ui.views import dashboard

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", dashboard),
]
