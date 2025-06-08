from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string


def generate_device_id(length=6):
    chars = string.ascii_letters + string.digits
    return "dev_" + "".join(random.choices(chars, k=length))


class iot_detail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    device_name = models.CharField("名称", max_length=50)
    device_id = models.CharField("ID", unique=True, default=generate_device_id, max_length=25)
    device_description = models.TextField("詳細", null=True, blank=True, max_length=100)
    threshold_notopen_hours = models.PositiveIntegerField(
        "未開閉アラート表示（時間）", default=24, validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    threshold_heartbeat_hours = models.PositiveIntegerField(
        "死活監視アラート表示（時間）", default=1, validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    heartbeat_timestamp = models.DateTimeField("最終更新時刻", null=True, blank=True)

    def __str__(self):
        return self.device_name
    
    class Meta:
        verbose_name = "デバイス"
        verbose_name_plural = "デバイス一覧"


class OpenCloseLog(models.Model):
    device = models.ForeignKey(
        iot_detail, on_delete=models.CASCADE, related_name="openclose_logs"
    )
    openclose_timestamp = models.DateTimeField("開閉時刻")
    status = models.CharField(
        "状態", max_length=10, choices=[("open", "開"), ("close", "閉")]
    )

    class Meta:
        ordering = ["-openclose_timestamp"]
        verbose_name = "ドア開閉履歴"
        verbose_name_plural = "ドア開閉履歴"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        logs = OpenCloseLog.objects.filter(device=self.device).order_by("-openclose_timestamp")
        if logs.count() > 10:
            for log in logs[10:]:
                log.delete()
