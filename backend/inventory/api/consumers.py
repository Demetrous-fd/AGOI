from asgiref.sync import sync_to_async
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer

from . import serializer
from .. import models


class ModelConsumerObserver(AsyncAPIConsumer):
    async def accept(self, **kwargs):
        await super().accept(**kwargs)
        await self.model_change.subscribe()

    @model_observer(models.ReportScannedItem, serializer_class=serializer.ReportScannedItemSerializer)
    async def model_change(self, message, action=None, **kwargs):
        # in this case since we subscribe int he `accept` method
        # we do not expect to have any `subscribing_request_ids` to loop over.
        if action == "create":
            instance = await sync_to_async(
                models.Instance.objects
                    .select_related("object")
                    .values_list("inventory_number", "object__name").get
            )(pk=message["instance"])
            message.update({
                "report": str(message["report"]),
                "id": str(message["instance"]),
                "number": instance[0],
                "name": instance[1]
            })
            del message["instance"]

            await self.reply(data=message, action=action)
