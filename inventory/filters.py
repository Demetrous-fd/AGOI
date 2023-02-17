from more_admin_filters import MultiSelectRelatedDropdownFilter, MultiSelectRelatedOnlyFilter
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.db.models import Q


class ConsumableBalanceFilter(admin.SimpleListFilter):
    title = "Баланс"
    parameter_name = 'balance'

    def lookups(self, request, model_admin):
        return (
            ('write_off', "Списанные"),
            ('on_balance', "На учете"),
        )

    def queryset(self, request, queryset):
        if self.value() == 'write_off':
            return queryset.filter(
                balance__lte=0,
            )
        if self.value() == 'on_balance':
            return queryset.filter(
                balance__gte=1,
            )


class InventoryNumberFilter(admin.SimpleListFilter):
    title = "Инвентарный номер"
    parameter_name = 'inventory_number'

    def lookups(self, request, model_admin):
        return (
            ("empty", "Без номера"),
            ("with_number", "С номером"),
        )

    def queryset(self, request, queryset):
        if self.value() == "empty":
            return queryset.filter(
                inventory_number__pk=1
            )
        if self.value() == "with_number":
            return queryset.filter(
                ~Q(inventory_number__pk=1)
            )


class MultiSelectFilter(MultiSelectRelatedDropdownFilter, MultiSelectRelatedOnlyFilter):
    pass


class ConstructNumberFilter(AutocompleteFilter):
    title = 'Номер контракта'
    field_name = 'contract_number'


class ObjectFilter(AutocompleteFilter):
    title = 'Объект'
    field_name = 'object'
