import uuid

from qr_code.templatetags.qr_code import qr_from_text
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.core import validators
from django.conf import settings
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
            f"<a href='{url}?object__id__exact={self.pk}'>Просмотр оборудования</a>"
        )
    show_instances_in_admin_view.short_description = ""

    def show_consumable_in_admin_view(self):
        url = reverse(f"admin:{self._meta.app_label}_{Consumable._meta.model_name}_changelist")
        return mark_safe(
            f"<a href='{url}?object__id__exact={self.pk}'>Просмотр расходников</a>"
        )
    show_consumable_in_admin_view.short_description = ""

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


class ContractNumber(models.Model):
    number = models.CharField(max_length=128, unique=True, verbose_name="Номер контракта")

    def __str__(self):
        return self.number

    def show_related_instances_in_admin_view(self):
        url = reverse(
            f"admin:{self._meta.app_label}_{Instance._meta.model_name}_changelist")
        return mark_safe(
            f"<a href='{url}?contract_number__id__exact={self.pk}'>Связанное оборудование</a>")
    show_related_instances_in_admin_view.short_description = ""

    def show_related_consumable_in_admin_view(self):
        url = reverse(
            f"admin:{self._meta.app_label}_{Consumable._meta.model_name}_changelist")
        return mark_safe(
            f"<a href='{url}?contract_number__id__exact={self.pk}'>Связанные расходники</a>")
    show_related_consumable_in_admin_view.short_description = ""

    class Meta:
        verbose_name = "Номер контракта"
        verbose_name_plural = "Номера контрактов"


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
    contract_number = models.ForeignKey(ContractNumber, on_delete=models.CASCADE, verbose_name="Номер контракта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        cascade_delete_history=True
    )

    def __str__(self):
        return f"{self.object.name}: {self.id}"

    def qr_preview(self):
        if settings.USE_QR_FULL_URI and settings.APP_DOMAIN:
            path = reverse(
                f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
                kwargs={"object_id": self.pk}
            )
            url = f"{settings.APP_DOMAIN}" + (f":{settings.APP_EXTERNAL_PORT}" if settings.APP_EXTERNAL_PORT else "")
            uri = f"{url}{path}"
            return qr_from_text(uri, size="T")
        return qr_from_text(f"{self.pk}", size="T")

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"


class ConsumableHistoryInfo(models.Model):
    written_off = models.IntegerField(
        validators=[validators.MinValueValidator(0)],
        verbose_name="Количество списаных расходников"
    )

    class Meta:
        abstract = True


class Consumable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, verbose_name="Объект")
    location = models.ForeignKey(
        Location, default=1, on_delete=models.SET_DEFAULT, verbose_name="Место нахождения")
    contract_number = models.ForeignKey(
        ContractNumber, on_delete=models.CASCADE, verbose_name="Номер контракта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    balance = models.IntegerField(
        default=10, validators=[validators.MinValueValidator(1)], verbose_name="Остаток")
    initial_quantity = models.IntegerField(
        default=10, validators=[validators.MinValueValidator(1)], verbose_name="Изначальное количество")
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True, verbose_name="Комментарий"),
        excluded_fields=("created_at", "object", "contract_number"),
        bases=(ConsumableHistoryInfo,),
        cascade_delete_history=True
    )

    def __str__(self):
        return f"{self.object.name}" if hasattr(self, "object") else str(self.pk)

    def show_balance(self):
        return f"{self.balance} / {self.initial_quantity}"
    show_balance.short_description = "Баланс"

    class Meta:
        verbose_name = "Расходник"
        verbose_name_plural = "Расходники"
