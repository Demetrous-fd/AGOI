import uuid

from qr_code.templatetags.qr_code import qr_from_text
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.core import validators
from django.conf import settings
from django.urls import reverse
from django.db import models


class EquipmentType(models.Model):
    name = models.CharField(max_length=128, verbose_name="Тип оборудования")

    def __str__(self):
        return self.name

    def show_related_instances_in_admin_view(self):
        url = reverse(
            f"admin:{self._meta.app_label}_{Instance._meta.model_name}_changelist")
        return mark_safe(
            f"<a class='button' href='{url}?equipment_type__id__exact={self.pk}'>Связанное оборудование</a>")
    show_related_instances_in_admin_view.short_description = ""

    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"


class Object(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, verbose_name="Название")
    short_name = models.CharField(max_length=32, verbose_name="Короткое название")
    slug = models.SlugField(max_length=128, unique=True, db_index=True, verbose_name="URL")
    equipment_type = models.ForeignKey(
        EquipmentType, null=True,
        on_delete=models.SET_NULL, verbose_name="Тип оборудования")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return f"{self.equipment_type}: {self.short_name}"

    def show_instances_in_admin_view(self):
        url = reverse(f"admin:{self._meta.app_label}_{Instance._meta.model_name}_changelist")
        return mark_safe(
            f"<a class='button' href='{url}?object__id__exact={self.pk}'>Просмотр оборудования</a>"
        )
    show_instances_in_admin_view.short_description = ""

    def show_consumable_in_admin_view(self):
        url = reverse(f"admin:{self._meta.app_label}_{Consumable._meta.model_name}_changelist")
        return mark_safe(
            f"<a class='button' href='{url}?object__id__exact={self.pk}'>Просмотр расходников</a>"
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
            f"<a class='button' href='{url}?contract_number__id__exact={self.pk}'>Связанное оборудование</a>")
    show_related_instances_in_admin_view.short_description = ""

    def show_related_consumable_in_admin_view(self):
        url = reverse(
            f"admin:{self._meta.app_label}_{Consumable._meta.model_name}_changelist")
        return mark_safe(
            f"<a class='button' href='{url}?contract_number__id__exact={self.pk}'>Связанные расходники</a>")
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
    inventory_number = models.CharField(
        max_length=32, default="Не указан", verbose_name="Инвентарный номер")
    object = models.ForeignKey(
        Object, on_delete=models.CASCADE, verbose_name="Объект")
    contract_number = models.ForeignKey(
        ContractNumber, on_delete=models.CASCADE, verbose_name="Номер контракта")
    owner = models.ForeignKey(
        Owner, default=1, null=True,
        on_delete=models.SET_NULL, verbose_name="Владелец")
    state = models.ForeignKey(
        State, default=1, null=True,
        on_delete=models.SET_NULL, verbose_name="Статус")
    location = models.ForeignKey(
        Location, default=1, null=True,
        on_delete=models.SET_NULL, verbose_name="Место нахождения")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        cascade_delete_history=True,
        excluded_fields=("comment", "object", "created_at"),
    )

    def get_qr_url(self):
        if settings.USE_QR_FULL_URI and settings.APP_DOMAIN:
            path = reverse(
                f"admin:{self._meta.app_label}_{self._meta.model_name}_change",
                kwargs={"object_id": self.pk}
            )
            url = f"{settings.APP_DOMAIN}" + (f":{settings.APP_EXTERNAL_PORT}" if settings.APP_EXTERNAL_PORT else "")
            uri = f"{url}{path}"
            return uri
        return str(self.pk)

    def qr_preview(self):
        return qr_from_text(self.get_qr_url(), size="T")

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
    contract_number = models.ForeignKey(
        ContractNumber, on_delete=models.CASCADE, verbose_name="Номер контракта")
    location = models.ForeignKey(
        Location, default=1, null=True,
        on_delete=models.SET_NULL, verbose_name="Место нахождения")
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
