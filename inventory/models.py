import uuid

from qr_code.templatetags.qr_code import qr_from_text
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.urls import reverse
from django.db import models


class Object(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(max_length=128, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="images", null=True, blank=True, verbose_name="Изображение")

    def __str__(self):
        return self.name

    def image_preview(self):
        if self.image:
            return mark_safe(f"<img src='{self.image.url}' width='256' />")
        return ""
    image_preview.short_description = "Предпросмотр"

    def show_instances_in_admin_view(self):
        url = reverse(f"admin:{self._meta.app_label}_{Instance._meta.model_name}_changelist")
        return mark_safe(
            f"<a href='{url}?object__id__exact={self.pk}'>Экземпляры объекта</a>"
        )
    show_instances_in_admin_view.short_description = ""

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"


class Address(models.Model):
    name = models.CharField(max_length=128, verbose_name="Адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class Location(models.Model):
    name = models.CharField(max_length=128, verbose_name="Помещение")
    address = models.ForeignKey(Address, default=1, on_delete=models.SET_DEFAULT, verbose_name="Адрес")

    def __str__(self):
        return f"{self.name}: {self.address}"

    class Meta:
        verbose_name = "Место нахождения"
        verbose_name_plural = "Локации"


class Owner(models.Model):
    first_name = models.CharField(max_length=32, verbose_name="Имя")
    second_name = models.CharField(max_length=32, verbose_name="Фамилия")
    last_name = models.CharField(max_length=32, verbose_name="Отчество")

    def __str__(self):
        return f"{self.second_name} {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class BatchCode(models.Model):
    code = models.CharField(max_length=128, unique=True, verbose_name="Код")

    def __str__(self):
        return self.code

    def show_related_instances_in_admin_view(self):
        url = reverse(
            f"admin:{self._meta.app_label}_{Instance._meta.model_name}_changelist")
        return mark_safe(
            f"<a href='{url}?batch_code__id__exact={self.pk}'>Связанное оборудование</a>")
    show_related_instances_in_admin_view.short_description = ""

    class Meta:
        verbose_name = "Код партии"
        verbose_name_plural = "Коды партий"


class State(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"


class Instance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, verbose_name="Объект")
    owner = models.ForeignKey(Owner, default=1, on_delete=models.SET_DEFAULT, verbose_name="Владелец")
    state = models.ForeignKey(State, default=1, on_delete=models.SET_DEFAULT, verbose_name="Статус")
    location = models.ForeignKey(Location, default=1, on_delete=models.SET_DEFAULT, verbose_name="Место нахождения")
    batch_code = models.ForeignKey(BatchCode, on_delete=models.CASCADE, verbose_name="Код партии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.object.name}: {self.id}"

    def qr_preview(self):
        return qr_from_text(f"{self.pk}", size="T")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
