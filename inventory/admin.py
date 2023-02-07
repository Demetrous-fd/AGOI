from operator import attrgetter
from datetime import datetime
from itertools import groupby

from django.contrib.admin.utils import quote
from django.urls import reverse
from simple_history.admin import SimpleHistoryAdmin
from django.forms.models import model_to_dict
from django.http.response import FileResponse
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import QuerySet

from . import models, forms, pdf


class ObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview", "id", "show_instances_in_admin_view")
    readonly_fields = ("image_preview",)
    prepopulated_fields = {
        "slug": ("name",)
    }


class ContractNumberAdmin(admin.ModelAdmin):
    list_display = ("number", "show_related_instances_in_admin_view")
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
        context = pdf.CreatePDFContext(items=data, page_size="A4")
        return FileResponse(pdf.create_pdf(context), as_attachment=True, filename="qr-codes.pdf")


class MixinSaveQrCodes:
    @admin.action(description="Скачать QR-коды оборудования")
    def download_qr_codes(self, request, queryset: QuerySet):
        queryset = queryset.order_by("contract_number")
        data = []
        for key, group_items in groupby(queryset, key=attrgetter("contract_number")):
            data.append(
                pdf.PDFBlock(
                    contract_number=key,
                    instances=tuple(group_items)
                )
            )
        context = pdf.CreatePDFContext(items=data, page_size="A4")
        return FileResponse(pdf.create_pdf(context), as_attachment=True, filename="qr-codes.pdf")


class MixinBulkSave:
    """Для работы требуется статический атрибут model в модели Admin"""
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


class InstanceAdmin(SimpleHistoryAdmin, MixinSaveQrCodes, MixinBulkSave):
    model = models.Instance
    form = forms.InstanceForm
    list_display = ("__str__", "owner", "location", "state", "contract_number", "created_at", "qr_preview")
    list_filter = ("object_id", "state", "contract_number")
    history_list_display = ("state", "location", "owner")
    search_fields = ("pk", "contract_number__number")
    readonly_fields = ("object", "contract_number", "qr_preview")
    actions = ("download_qr_codes",)

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


class ConsumableAdmin(MixinSaveQrCodes, MixinBulkSave, SimpleHistoryAdmin):
    model = models.Consumable
    form = forms.ConsumableForm
    list_display = ("__str__", "owner", "location", "state", "contract_number", "created_at", "qr_preview")
    list_filter = ("object_id", "state", "contract_number")
    history_list_display = ("state", "location", "owner")
    search_fields = ("pk", "contract_number__number")
    readonly_fields = ("object", "contract_number", "state", "qr_preview")
    actions = ("download_qr_codes",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_form(self, request, obj=None, change=False, **kwargs):
        default = {}
        if obj is None:  # On create view
            default["form"] = forms.ConsumableAddBulkForm
        default.update(kwargs)
        return super().get_form(request, obj, change, **default)


admin.site.register(models.Object, ObjectAdmin)
admin.site.register(models.Instance, InstanceAdmin)
admin.site.register(models.Consumable, ConsumableAdmin)
admin.site.register(models.ContractNumber, ContractNumberAdmin)
admin.site.register(models.State)
admin.site.register(models.Address)
admin.site.register(models.Location)
admin.site.register(models.Owner)
