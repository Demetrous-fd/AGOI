from django.db import transaction
from django.utils import timezone


@transaction.atomic
def update_with_history(queryset, user, update_data: dict, history_data: dict, history_change_reason: str = ""):
    """
    Since queryset.update does not trigger post_save signals, which django-simple-history uses,
    we manually create the history records here alongside the update
    """
    queryset.update(**update_data)

    obj = queryset.get()
    history_model = obj.history.model
    exclude_fields = history_model._history_excluded_fields
    fields = [field for field in obj._meta.get_fields() if field.name not in exclude_fields]
    fields_with_data = {field.name: getattr(obj, field.name) for field in fields}

    history_model.objects.create(
        history_user=user,
        history_date=timezone.now(),
        history_change_reason=history_change_reason,
        history_type='~',
        **fields_with_data,
        **history_data
    )
