from dal import autocomplete
from django import forms

from . import models


class ObjectForm(forms.ModelForm):
    class Meta:
        model = models.Object
        fields = "__all__"
        widgets = {
            "equipment_type": autocomplete.ModelSelect2(url='autocomplete-equipment-type'),
        }


class InstanceForm(forms.ModelForm):
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
    count = forms.IntegerField(min_value=1, initial=1, label="Количество")

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
        exclude = ("balance", )


class ConsumableWriteOff(forms.Form):
    count = forms.IntegerField(min_value=1, initial=1, label="Количество списываемых расходников")
    comment = forms.CharField(required=False, widget=forms.Textarea, label="Комментарий")
