from iot_app.models import Iot_detail
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from datetime import timedelta

# Create your views here.


@method_decorator(never_cache, name="dispatch")
class IoTList(LoginRequiredMixin, TemplateView):
    template_name = "iot_app/iot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device"] = Iot_detail.objects.filter(user=self.request.user).first()

        if context["device"]:
            now_time = now()

            heartbeat_ok = True
            heartbeat_exist = True
            if context["device"].heartbeat_timestamp:
                diff = now_time - context["device"].heartbeat_timestamp
                heartbeat_ok = diff <= timedelta(
                    hours=context["device"].threshold_heartbeat_hours
                )
            else:
                heartbeat_exist = False

            openclose_ok = True
            openclose_exist = True
            latest_log = context["device"].openclose_logs.first()
            if latest_log and latest_log.openclose_timestamp:
                diff = now_time - latest_log.openclose_timestamp
                openclose_ok = diff <= timedelta(
                    hours=context["device"].threshold_notopen_hours
                )
            else:
                openclose_exist = False

            context["openclose_ok"] = openclose_ok
            context["heartbeat_ok"] = heartbeat_ok
            context["openclose_exist"] = openclose_exist
            context["heartbeat_exist"] = heartbeat_exist
            context["latest_log"] = latest_log
            context["openclose_logs"] = context["device"].openclose_logs.all()[1:5]

        return context


@method_decorator(never_cache, name="dispatch")
class IoTCreate(LoginRequiredMixin, CreateView):
    model = Iot_detail
    fields = ["device_name", "device_id", "device_description"]
    success_url = reverse_lazy("iot")
    template_name = "iot_app/iot_form.html"
    context_object_name = "iot_detail"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = False
        context["iot_detail"] = Iot_detail.objects.filter(user=self.request.user).first()
        return context


@method_decorator(never_cache, name="dispatch")
class IoTUpdate(LoginRequiredMixin, UpdateView):
    model = Iot_detail
    fields = ["device_name", "device_id", "device_description"]
    success_url = reverse_lazy("iot")
    template_name = "iot_app/iot_form.html"
    context_object_name = "iot_detail"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context

    def get_object(self):
        return Iot_detail.objects.filter(user=self.request.user).first()


@method_decorator(never_cache, name="dispatch")
class IoTDelete(LoginRequiredMixin, DeleteView):
    model = Iot_detail
    success_url = reverse_lazy("iot")
    template_name = "iot_app/iot_delete.html"
    context_object_name = "iot_detail"

    def get_object(self):
        return Iot_detail.objects.filter(user=self.request.user).first()


@method_decorator(never_cache, name="dispatch")
class TimeEdit(LoginRequiredMixin, UpdateView):
    model = Iot_detail
    fields = ["threshold_notopen_hours", "threshold_heartbeat_hours"]
    success_url = reverse_lazy("iot")
    template_name = "iot_app/iot_form.html"
    context_object_name = "iot_detail"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_update"] = True
        return context

    def get_object(self):
        return Iot_detail.objects.filter(user=self.request.user).first()


@method_decorator(never_cache, name="dispatch")
class IoTListLogin(LoginView):
    template_name = "iot_app/login.html"

    def get_success_url(self):
        return reverse_lazy("iot")


@method_decorator(never_cache, name="dispatch")
class RegisterIoTApp(FormView):
    form_class = UserCreationForm
    success_url = reverse_lazy("iot")
    template_name = "iot_app/register.html"

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


@method_decorator(never_cache, name="dispatch")
class AccountDelete(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("login")
    template_name = "iot_app/account_delete.html"

    def get_object(self):
        return self.request.user
