from django.urls import path

from . import views

urlpatterns = [
    path("autocomplete/batch-code", views.BatchCodeAutocomplete.as_view(), name="autocomplete-batch-code"),
    path("autocomplete/location", views.LocationAutocomplete.as_view(), name="autocomplete-location"),
    path("autocomplete/state", views.StateAutocomplete.as_view(), name="autocomplete-state"),
    path("autocomplete/owner", views.OwnerAutocomplete.as_view(), name="autocomplete-owner"),
    path("autocomplete/object", views.ObjectAutocomplete.as_view(), name="autocomplete-object"),
]
