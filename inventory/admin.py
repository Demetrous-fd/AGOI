from operator import attrgetter
from itertools import groupby
from datetime import datetime

from django.http.response import FileResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from simple_history.admin import SimpleHistoryAdmin
from rangefilter.filters import DateRangeFilter
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.contrib.admin.utils import quote
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import QuerySet, F
from django.urls import reverse, path


from .filters import ConsumableBalanceFilter, MultiSelectFilter, ConstructNumberFilter, ObjectFilter
from .history import update_with_history
from . import models, forms, pdf
from AGOI.admin import site
from .pdf import PageSize


class ObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview", "id", "show_instances_in_admin_view", "show_consumable_in_admin_view")
    readonly_fields = ("image_preview",)
    search_fields = ("name",)
    prepopulated_fields = {
        "slug": ("name",)
    }


class ContractNumberAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "show_related_instances_in_admin_view",
        "show_related_consumable_in_admin_view"
    )
    search_fields = ("number",)
    actions = ["download_qr_codes"]

    @admin.action(description="Скачать QR-коды оборудования из партии")
    def download_qr_codes(self, request, queryset):
        data = []
        for item in queryset:
            instances = models.Instance.objects.filter(contract_number__pk=item.pk)
            data.append(
                pdf.PDFBlock(
                    contract_number=item.number,
                    instances=instances.all()
                )
            )
        context = pdf.PDFContext(items=data, page_size="A4")
        return FileResponse(pdf.create_pdf(context), as_attachment=True, filename="qr-codes.pdf")


class InstanceAdmin(SimpleHistoryAdmin):
    model = models.Instance
    form = forms.InstanceForm
    list_display = ("__str__", "owner", "location", "contract_number", "state", "created_at", "qr_preview")
    list_filter = (
        ("state", MultiSelectFilter),
        ("created_at", DateRangeFilter),
        ObjectFilter,
        ConstructNumberFilter,
    )
    history_list_display = ("location", "owner")
    search_fields = ("pk", "contract_number__number")
    readonly_fields = ("object", "contract_number", "qr_preview")
    actions = ("download_qr_codes_2824", "download_qr_codes_a4")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_form(self, request, obj=None, change=False, **kwargs):
        default = {}
        if obj is None:  # On create view
            default["form"] = forms.InstanceAddBulkForm
        default.update(kwargs)
        return super().get_form(request, obj, change, **default)

    @admin.action(description="Скачать QR-коды оборудования для печати на LP 2824 Plus")
    def download_qr_codes_2824(self, request, queryset: QuerySet):
        return self.create_pdf_with_qr_codes(queryset, page_size=PageSize.LP2824_PLUS)

    @admin.action(description="Скачать QR-коды оборудования в формате A4")
    def download_qr_codes_a4(self, request, queryset: QuerySet):
        return self.create_pdf_with_qr_codes(queryset, page_size=PageSize.A4)

    @staticmethod
    def create_pdf_with_qr_codes(queryset: QuerySet, page_size: PageSize):
        queryset = queryset.order_by("contract_number")
        data = []
        for key, group_items in groupby(queryset, key=attrgetter("contract_number")):
            data.append(
                pdf.PDFBlock(
                    contract_number=key,
                    instances=tuple(group_items)
                )
            )
        context = pdf.PDFContext(items=data, page_size=page_size)
        return FileResponse(pdf.create_pdf(context), as_attachment=True, filename="qr-codes.pdf")

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        opts = self.model._meta
        count = form.cleaned_data["count"]
        fields_with_foreign_key_type = [
            field.name for field in obj._meta.fields if field.get_internal_type() == "ForeignKey"
        ]
        obj_other_fields = model_to_dict(obj, exclude=fields_with_foreign_key_type)
        obj_foreign_key_fields = {
            f"{key}_id": value
            for key, value in model_to_dict(obj, fields=fields_with_foreign_key_type).items()
        }
        obj_pk = obj.pk
        obj = obj_other_fields
        obj.update(obj_foreign_key_fields)
        obj["created_at"] = datetime.now()
        for index in range(count):
            if index == 0:
                new_obj = self.model(pk=obj_pk, **obj)
            else:
                new_obj = self.model(**obj)

                obj_url = reverse(
                    'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                    args=(quote(new_obj.pk),),
                    current_app=self.admin_site.name,
                )
                obj_url = format_html(f"<a href='{obj_url}'>{new_obj}</a>")
                msg = format_html(
                    f"{opts.verbose_name} “{obj_url}” был успешно добавлен."
                )
                self.message_user(request, msg, messages.SUCCESS)
            new_obj.save()


class ConsumableAdmin(SimpleHistoryAdmin):
    form = forms.ConsumableForm
    list_display = ("__str__", "show_balance", "location", "contract_number", "created_at", "account_actions")
    list_filter = (
        ConsumableBalanceFilter,
        ("created_at", DateRangeFilter),
        ObjectFilter,
        ConstructNumberFilter,
    )
    history_list_display = ("location", "written_off", "balance", "initial_quantity")
    search_fields = ("pk", "contract_number__number")
    readonly_fields = ("object", "contract_number", "show_balance", "initial_quantity", "balance", "account_actions")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_form(self, request, obj=None, change=False, **kwargs):
        default = {}
        if obj is None:  # On create view
            default["form"] = forms.ConsumableAdd
        default.update(kwargs)
        return super().get_form(request, obj, change, **default)

    def save_model(self, request, obj: models.Consumable, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        obj.balance = obj.initial_quantity
        super().save_model(request, obj, form, change)

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Выдать расходники</a>&nbsp;',
            reverse('admin:consumable-write-off', args=[obj.pk])
        )
    account_actions.short_description = 'Действия'
    account_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'consumable/<str:pk>/write-off',
                self.write_off_consumable_view,
                name="consumable-write-off"
            ),
        ]
        return my_urls + urls

    def write_off_consumable_view(self, request, pk: str):
        obj = get_object_or_404(models.Consumable, pk=pk)

        if request.method == 'POST':
            form = forms.ConsumableWriteOff(request.POST)
            if form.is_valid():
                written_off = form.cleaned_data["count"]
                comment = form.cleaned_data["comment"]
                if obj.balance - written_off >= 0:
                    queryset = models.Consumable.objects.filter(pk=pk)
                    update_data = {"balance": F("balance") - written_off}
                    history_data = {"written_off": written_off}
                    update_with_history(
                        queryset, request.user, update_data, history_data, history_change_reason=comment
                    )
                    self.message_user(request, f'Расходники в количестве: {written_off} выданы')
                else:
                    self.message_user(
                        request, 'Невозможно выдать больше расходников чем имеется на балансе', level="Warning"
                    )
                url = reverse(
                    f"admin:inventory_{models.Consumable._meta.model_name}_changelist"
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        if request.method != "POST":
            form = forms.ConsumableWriteOff()

        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = "Списание расходников"
        context['balance'] = obj.balance
        return TemplateResponse(
            request,
            'admin/action/write_off.html',
            context,
        )


site.register(models.Object, ObjectAdmin)
site.register(models.Instance, InstanceAdmin)
site.register(models.Consumable, ConsumableAdmin)
site.register(models.ContractNumber, ContractNumberAdmin)
site.register(models.State)
site.register(models.Address)
site.register(models.Location)
site.register(models.Owner)
