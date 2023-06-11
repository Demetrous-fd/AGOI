from asgiref.sync import sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer

from . import serializer
from .. import models


class ModelConsumerObserver(AsyncAPIConsumer):
    async def accept(self, **kwargs):
        await super().accept(**kwargs)
        await self.report_item_change.subscribe()
        await self.report_change.subscribe()

    @model_observer(models.ReportScannedItem, serializer_class=serializer.ReportScannedItemSerializer)
    async def report_item_change(self, message, action=None, **kwargs):
        # in this case since we subscribe int he `accept` method
        # we do not expect to have any `subscribing_request_ids` to loop over.
        if action == "create":
            instance = await sync_to_async(
                models.Instance.objects
                    .select_related("object")
                    .values_list("inventory_number", "object__name").get
            )(pk=message["instance"])
            message.update({
                "id": str(message["report"]),
                "instanceId": str(message["instance"]),
                "number": instance[0],
                "name": instance[1],
                "model": "report-item"
            })
            del message["instance"]
            del message["report"]

            await self.reply(data=message, action=action)

    @model_observer(models.Report, serializer_class=serializer.ReportSerializer)
    async def report_change(self, message, action=None, **kwargs):
        if action == "update":
            message.update({"model": "report"})
            await self.reply(data=message, action=action)
