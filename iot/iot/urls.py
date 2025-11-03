from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("iot_app.urls")),
    path("admin_iot_app/", admin.site.urls),
]
