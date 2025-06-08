from .views import (
    IoTList,
    IoTCreate,
    IoTUpdate,
    IoTDelete,
    IoTListLogin,
    RegisterIoTApp,
    TimeEdit,
    AccountDelete,
)
from django.contrib.auth.views import LogoutView
from django.urls import path

urlpatterns = [
    path("", IoTList.as_view(), name="iot"),
    path("create-iot", IoTCreate.as_view(), name="create-iot"),
    path("edit-iot", IoTUpdate.as_view(), name="edit-iot"),
    path("delete-iot", IoTDelete.as_view(), name="delete-iot"),
    path("time-edit", TimeEdit.as_view(), name="time-edit"),
    path("login", IoTListLogin.as_view(), name="login"),
    path("logout", LogoutView.as_view(next_page="login"), name="logout"),
    path("register", RegisterIoTApp.as_view(), name="register"),
    path("account-delete/", AccountDelete.as_view(), name="account-delete"),
]
