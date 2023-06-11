from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from . import views, consumers


router = DefaultRouter()
router.register("api/v1/report", views.ReportView, basename='report')
router.register("api/v1/instance", views.InstanceView, basename='instance')
# router.register("api/v1/report-scanned-item", views.ReportScannedItemView, basename='r')


urlpatterns = [
    path("api/v1/address/", views.AddressView.as_view()),
    # re_path("^api/v1/location/(?P<address>.+)/$", views.LocationView.as_view()),
    path("api/v1/location/", views.LocationView.as_view()),
    path("", include(router.urls))
]

websocket_urlpatterns = [
    re_path("^ws/$", consumers.ModelConsumerObserver.as_asgi()),
]
