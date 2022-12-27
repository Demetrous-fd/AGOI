from dal import autocomplete
from django import forms

from . import models


class InstanceForm(forms.ModelForm):
    class Meta:
        model = models.Instance
        fields = "__all__"
        widgets = {
            "location": autocomplete.ModelSelect2(url='autocomplete-location'),
            "batch_code": autocomplete.ModelSelect2(url='autocomplete-batch-code'),
            "state": autocomplete.ModelSelect2(url='autocomplete-state'),
            "owner": autocomplete.ModelSelect2(url='autocomplete-owner'),
            "object": autocomplete.ModelSelect2(url='autocomplete-object'),
        }


class InstanceAddBulkForm(InstanceForm):
    count = forms.IntegerField(min_value=1, initial=1, label="Количество")
