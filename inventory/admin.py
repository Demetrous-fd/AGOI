from datetime import datetime

from simple_history.admin import SimpleHistoryAdmin
from django.forms.models import model_to_dict
from django.http.response import FileResponse
from django.contrib import admin

from . import models, forms, pdf


class ObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview", "id", "show_instances_in_admin_view")
    readonly_fields = ("image_preview",)
    prepopulated_fields = {
        "slug": ("name",)
    }


class BatchCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "show_related_instances_in_admin_view")
    actions = ["download_qr_codes"]

    @admin.action(description="Скачать QR-коды оборудования")
    def download_qr_codes(self, request, queryset):
        data = []
        for item in queryset:
            instances = models.Instance.objects.filter(batch_code__pk=item.pk)
            object_name = instances.first().object.name
            data.append(
                pdf.PDFBlock(
                    object=object_name,
                    batch_code=item.code,
                    instances=instances.all()
                )
            )
        context = pdf.CreatePDFContext(items=data, page_size="A5")
        return FileResponse(pdf.create_pdf(context), as_attachment=False, filename="test.pdf")


class InstanceAdmin(SimpleHistoryAdmin):
    list_display = ("__str__", "owner", "location", "state", "batch_code", "created_at", "qr_preview")
    list_filter = ("object_id", "state", "batch_code")
    history_list_display = ("state", "location", "owner")
    search_fields = ("pk", "batch_code__code")
    readonly_fields = ("object", "batch_code")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        else:
            return []

    def get_form(self, request, obj=None, change=False, **kwargs):
        default = {}
        if obj is None:
            default["form"] = forms.InstanceAddBulkForm
        default.update(kwargs)
        return super().get_form(request, obj, change, **default)

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            count = form.cleaned_data["count"]
            fields_with_foreign_key_type = [
                field.name for field in obj._meta.fields if field.get_internal_type() == "ForeignKey"
            ]
            obj_other_fields = model_to_dict(obj, exclude=fields_with_foreign_key_type)
            obj_foreign_key_fields = {
                f"{key}_id": value
                for key, value in model_to_dict(obj, fields=fields_with_foreign_key_type).items()
            }
            obj = obj_other_fields
            obj.update(obj_foreign_key_fields)
            obj["created_at"] = datetime.now()
            for _ in range(count):
                new_obj = models.Instance(**obj)
                super().save_model(request, new_obj, form, change)


admin.site.register(models.Object, ObjectAdmin)
admin.site.register(models.Instance, InstanceAdmin)
admin.site.register(models.BatchCode, BatchCodeAdmin)
admin.site.register(models.State)
admin.site.register(models.Address)
admin.site.register(models.Location)
admin.site.register(models.Owner)
