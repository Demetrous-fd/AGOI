from collections import defaultdict
from itertools import chain
from functools import wraps
import uuid

from rest_framework import generics, mixins, viewsets, status
from django.http import Http404, QueryDict, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Count, F
from django.conf import settings
from zoneinfo import ZoneInfo

from ..table import TableBuilder
from . import serializer
from .. import models


class DualSerializerViewSet(viewsets.ModelViewSet):
    # mapping serializer into the action
    serializer_classes = {}

    # serializer_classes = {
    #     'list': serializers.ListaGruppi,
    #     'retrieve': serializers.DettaglioGruppi,
    #     # ... other actions
    # }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)


class AddressView(generics.ListAPIView):
    serializer_class = serializer.AddressSerializer

    def get_queryset(self):
        queryset = models.Address.objects.all()
        not_empty = self.request.query_params.get("not_empty")
        if not_empty == "1":
            queryset = queryset.filter(
                id__in=models.Location.objects.values_list("address_id", flat=True).distinct()
            )
        return queryset


class LocationView(generics.ListAPIView):
    serializer_class = serializer.LocationSerializer

    def get_queryset(self):
        queryset = models.Location.objects.all()
        address_id: str = self.request.query_params.get("address")
        if address_id and address_id.isnumeric():
            queryset = queryset.filter(address__pk=address_id)
        return queryset


class ReportView(DualSerializerViewSet):
    queryset = models.Report.objects.order_by('-created_at').all()
    serializer_class = serializer.ReportSerializer
    serializer_classes = {
        "list": serializer.ReportRetrieveSerializer,
        "item": serializer.ReportScannedItemSerializer,
        "retrieve": serializer.ReportGetSerializer
    }

    @staticmethod
    def block_finished_report(func):
        @wraps(func)
        def wrapper(view, request, *args, **kwargs):
            report = get_object_or_404(models.Report, pk=kwargs.get("pk", None))
            if report.status == "finish":
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return func(view, request, *args, **kwargs)

        return wrapper

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = serializer.save()

        instances = models.Instance.objects.filter(
            created_at__lte=report.created_at, location=report.location
        ).values_list("id", flat=True)

        models.ReportItem.objects.bulk_create(
            [models.ReportItem(instance_id=instance, report_id=report.id) for instance in instances]
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["GET"], url_path="item/count")
    def count(self, request: Request, pk=None):
        try:
            uuid.UUID(pk)
        except ValueError:
            raise Http404

        instances = models.ReportItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)

        queryset = models.Instance.objects.select_related("object").filter(
            id__in=instances).values(name=F("object__name")).annotate(count=Count("*"))

        instances = models.Instance.objects.select_related("object").filter(id__in=instances).order_by(
            "object").values_list(F("object__name"), "id", "inventory_number")

        grouped_instances_by_object = defaultdict(list)
        for object_name, instance_id, inventory_number in instances:
            grouped_instances_by_object[object_name].append({"id": instance_id, "number": inventory_number})

        for data in queryset:
            data.update({"ids": grouped_instances_by_object[data["name"]]})

        return Response(queryset)

    @action(detail=True, methods=["GET"], url_path="download")
    def download(self, request: Request, pk=None):
        report = get_object_or_404(models.Report, pk=pk)
        if report.status != "finish":
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(content_type='application/ms-excel')
        filename = f"{report.location}_{report.created_at.strftime('%d.%m.%Y')}"
        response['Content-Disposition'] = f'attachment; ' \
                                          f'filename="{filename}.xlsx";'.encode("utf-8")

        table = TableBuilder("Отчёт")
        table.add_line((
            'Дата начала',
            report.created_at.replace(tzinfo=ZoneInfo(settings.TIME_ZONE)).strftime('%d.%m.%Y %H:%M')
        ))
        table.add_line((
            'Дата окончания',
            report.updated_at.replace(tzinfo=ZoneInfo(settings.TIME_ZONE)).strftime('%d.%m.%Y %H:%M')
        ))
        table.add_line(('Адрес', report.location.address.name))
        table.add_line(('Помещение', report.location.name))
        table.add_line([])
        table.add_line(('Наименование', "На учете", "Отсканировано"))
        items = defaultdict(lambda: dict(count=0, scanned=0))

        # Количество оборудования на учете
        instances = models.ReportItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)
        queryset1 = models.Instance.objects.select_related("object").order_by("object").filter(
            id__in=instances).values(name=F("object__name")).annotate(count=Count("*"))
        for _object in queryset1:
            items[_object["name"]]["count"] = _object["count"]

        # Отсканированное оборудование
        scanned_instances = models.ReportScannedItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)
        scanned_unknown_instances = scanned_instances.exclude(instance_id__in=instances).values_list("instance_id",
                                                                                                     flat=True)
        queryset2 = models.Instance.objects.select_related("object").filter(
            id__in=scanned_instances
        ).exclude(
            id__in=scanned_unknown_instances
        ).order_by(
            "object"
        ).values(name=F('object__name')).annotate(scanned=Count('*'))
        for _object in queryset2:
            items[_object["name"]]["scanned"] = _object["scanned"]

        if scanned_unknown_instances:
            items["Не соответствующее месту нахождения"] = {
                "count": "",
                "scanned": len(scanned_unknown_instances)
            }

        for key in items:
            table.add_line([key, *items[key].values()])

        table.set_page("Оборудование")
        table.add_line(["Отсканированное оборудование"])
        table.add_line(["Наименование", "Инвентарные номера"])
        items = defaultdict(list)
        for key, number in models.Instance.objects.filter(
                id__in=scanned_instances
            ).exclude(
                id__in=scanned_unknown_instances
        ).values_list("object__name", "inventory_number"):
            items[key].append(number)

        for key, number in models.Instance.objects.filter(
                id__in=scanned_unknown_instances
        ).values_list("object__name", "inventory_number"):
            items[f"{key}-unknown"].append(number)

        for key in items:
            if "-unknown" in key:
                table.add_line([])
                table.add_line(["Не соответствующее месту нахождения"])
                table.add_line(["Наименование", "Инвентарные номера"])
            table.add_line([key.replace("-unknown", ""), "\r\n".join(items[key])], [2])

        table.write(response)
        return response

    @action(detail=True, methods=["GET"], url_path="item/scanned")
    def scanned(self, request: Request, pk=None):
        try:
            uuid.UUID(pk)
        except ValueError:
            raise Http404

        queryset = models.ReportScannedItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)
        return Response(queryset)

    @action(detail=True, methods=["GET"], url_path="item/scanned/count")
    def scanned_count(self, request: Request, pk=None):
        try:
            uuid.UUID(pk)
        except ValueError:
            raise Http404

        instances = models.ReportItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)
        scanned_instances = models.ReportScannedItem.objects.filter(report_id=pk).values_list("instance_id", flat=True)
        scanned_unknown_instances = scanned_instances.exclude(instance_id__in=instances).values_list("instance_id",
                                                                                                     flat=True)

        queryset = models.Instance.objects.select_related("object").filter(
            id__in=scanned_instances
        ).exclude(
            id__in=scanned_unknown_instances
        ).values(name=F('object__name')).annotate(currentCount=Count('*'))

        combined_queryset = list(chain(queryset, [
            {"name": "unknown", "currentCount": len(scanned_unknown_instances), "ids": [
                {"id": instance[0], "number": instance[1]} for instance in models.Instance.objects.filter(
                    id__in=scanned_unknown_instances
                ).values_list("id", "inventory_number")
            ]}
        ]))
        return Response(combined_queryset)

    @action(detail=True, methods=["POST"])
    @block_finished_report
    def item(self, request: Request, pk=None):
        if isinstance(request.data, QueryDict):
            data = request.data.dict()
        else:
            data = request.data

        data["report"] = pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.validated_data["instance"]
        if models.ReportScannedItem.objects.filter(report_id=pk, instance_id=instance.id).first():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            models.ReportItem.objects.get(report_id=pk, instance=instance)
        except ObjectDoesNotExist:
            serializer.validated_data["status"] = "error"

        serializer.save()

        headers = self.get_success_headers(serializer.data)

        instance = models.Instance.objects.select_related("object").get(pk=instance.id)
        result = {
            "status": serializer.data["status"],
            "name": instance.object.name,
            "number": instance.inventory_number,
        }
        return Response(result, status=status.HTTP_201_CREATED, headers=headers)

    @block_finished_report
    def update(self, request, *args, **kwargs):
        return super(ReportView, self).update(request, *args, **kwargs)

    @block_finished_report
    def partial_update(self, request, *args, **kwargs):
        return super(ReportView, self).partial_update(request, *args, **kwargs)


class InstanceView(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializer.InstanceSerializer

    @action(detail=True, methods=["GET"])
    def count(self, request: Request, pk=None):
        if not pk.isnumeric():
            raise Http404

        queryset = models.Instance.objects.filter(
            location_id=pk).values(name=F('object__name')).annotate(count=Count('*'))
        return Response(queryset)
