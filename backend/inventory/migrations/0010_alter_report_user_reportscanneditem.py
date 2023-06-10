# Generated by Django 4.0.10 on 2023-06-02 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0009_remove_report_finished_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ReportScannedItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('ok', 'OK'), ('error', 'Не был в списке инвентаризации')], default='in_progress', max_length=8)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.instance')),
                ('report', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='scanned_items', to='inventory.report')),
            ],
        ),
    ]