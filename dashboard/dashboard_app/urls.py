from django.contrib import admin
from django.urls import include, path
from ui.views import dashboard, kafka_tail, service_state

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("api/state/", service_state, name="service-state"),
    path("api/kafka-tail/<str:stream>/", kafka_tail, name="kafka-tail"),
]
