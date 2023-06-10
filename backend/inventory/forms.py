from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError

from . import models


class ObjectForm(forms.ModelForm):
    class Meta:
        model = models.Object
        fields = "__all__"
        widgets = {
            "equipment_type": autocomplete.ModelSelect2(url='autocomplete-equipment-type'),
        }


class InstanceForm(forms.ModelForm):
    def clean(self):
        if "inventory_number" in self.changed_data:
            change = self.data["inventory_number"]
            if models.Instance.objects.filter(inventory_number=change).count():
                raise ValidationError("!!! Оборудование с таким инвентарным номером уже существует !!!")

        if "inventory_numbers" in self.changed_data:
            exists_instance = models.Instance.objects.filter(
                inventory_number__in=[number.strip() for number in self.data["inventory_numbers"].split("\n")]
            ).values_list("inventory_number", flat=True).all()
            raise ValidationError(
                [
                    ValidationError(value, code=index) for index, value in enumerate([
                    "!!! Оборудование с таким инвентарным номером уже существует !!!",
                    *[f"- {number}" for number in exists_instance]])
                ]
            )

        return super().clean()

    class Meta:
        model = models.Instance
        fields = "__all__"
        widgets = {
            "location": autocomplete.ModelSelect2(url='autocomplete-location'),
            "contract_number": autocomplete.ModelSelect2(url='autocomplete-contract-number'),
            "state": autocomplete.ModelSelect2(url='autocomplete-state'),
            "owner": autocomplete.ModelSelect2(url='autocomplete-owner'),
            "object": autocomplete.ModelSelect2(url='autocomplete-object'),
        }


class InstanceAddBulkForm(InstanceForm):
    inventory_numbers = forms.CharField(
        widget=forms.Textarea,
        required=True,
        label="Инвентарные номера",
        help_text="Разделяйте инвентарные номера переносом строки"
    )

    class Meta(InstanceForm.Meta):
        exclude = ("inventory_number", "owner")


class ConsumableForm(forms.ModelForm):
    class Meta:
        model = models.Consumable
        fields = "__all__"
        widgets = {
            "location": autocomplete.ModelSelect2(url='autocomplete-location'),
            "contract_number": autocomplete.ModelSelect2(url='autocomplete-contract-number'),
            "object": autocomplete.ModelSelect2(url='autocomplete-object'),
        }


class ConsumableAdd(ConsumableForm):
    initial_quantity = forms.IntegerField(min_value=1, initial=1, label="Изначальное количество")

    class Meta(ConsumableForm.Meta):
        exclude = ("balance",)


class ConsumableWriteOff(forms.Form):
    count = forms.IntegerField(min_value=1, initial=1, label="Количество списываемых расходников")
    comment = forms.CharField(required=False, widget=forms.Textarea, label="Комментарий")
