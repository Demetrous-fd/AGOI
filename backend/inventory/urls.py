from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.urls import path

from AGOI import settings
from . import views
from .api import urls

urlpatterns = [
    path("", RedirectView.as_view(url=settings.FRONTEND_URL)),
    path("autocomplete/contract-number", login_required(views.ContractNumberAutocomplete.as_view()),
         name="autocomplete-contract-number"),
    path("autocomplete/equipment-type", login_required(views.EquipmentTypeAutocomplete.as_view()),
         name="autocomplete-equipment-type"),
    path("autocomplete/location", login_required(views.LocationAutocomplete.as_view()),
         name="autocomplete-location"),
    path("autocomplete/state", login_required(views.StateAutocomplete.as_view()),
         name="autocomplete-state"),
    path("autocomplete/owner", login_required(views.OwnerAutocomplete.as_view()),
         name="autocomplete-owner"),
    path("autocomplete/object", login_required(views.ObjectAutocomplete.as_view()),
         name="autocomplete-object"),
    path("autocomplete/instance", login_required(views.InstanceAutocomplete.as_view()),
         name="autocomplete-instance")
] + urls.urlpatterns

websocket_urlpatterns = urls.websocket_urlpatterns
