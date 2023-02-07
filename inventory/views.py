from functools import reduce
from operator import or_

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from dal import autocomplete

from . import models


# Create your views here.

@login_required
def search(request):
    return render(request, "inventory/search.html")


def _get_queryset_for_autocomplete(request, query, model, fields: list[str]):
    if not request.user.is_authenticated:
        return model.objects.none()

    qs = model.objects.all()
    filter_args = (Q(**{f"{field}__istartswith": query}) for field in fields)
    if query:
        qs = qs.filter(reduce(or_, filter_args))

    return qs


class ContractNumberAutocomplete(autocomplete.Select2QuerySetView):
    create_field = "number"
    validate_create = True

    def get_queryset(self):
        return _get_queryset_for_autocomplete(self.request, self.q, models.ContractNumber, ["number"])


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    create_field = "name"
    validate_create = True

    def get_queryset(self):
        return _get_queryset_for_autocomplete(
            self.request, self.q, models.Location, ["name", "address__name"])


class StateAutocomplete(autocomplete.Select2QuerySetView):
    create_field = "name"
    validate_create = True

    def get_queryset(self):
        return _get_queryset_for_autocomplete(self.request, self.q, models.State, ["name"])


class OwnerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        return _get_queryset_for_autocomplete(
            self.request, self.q, models.Owner, ["first_name", "second_name", "last_name"])


class ObjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        return _get_queryset_for_autocomplete(self.request, self.q, models.Object, ["name"])


class InstanceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        return _get_queryset_for_autocomplete(
            self.request, self.q, models.Instance,
            ["object__name", "id", "contract_number__number"]
        )
