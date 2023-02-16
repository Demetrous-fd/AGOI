from more_admin_filters import MultiSelectRelatedDropdownFilter, MultiSelectRelatedOnlyFilter
from admin_auto_filters.filters import AutocompleteFilter, AutocompleteSelect
from django.contrib import admin


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


class MultiSelectFilter(MultiSelectRelatedDropdownFilter, MultiSelectRelatedOnlyFilter):
    pass


class ConstructNumberFilter(AutocompleteFilter):
    title = 'Номер контракта'
    field_name = 'contract_number'


class ObjectFilter(AutocompleteFilter):
    title = 'Объект'
    field_name = 'object'
