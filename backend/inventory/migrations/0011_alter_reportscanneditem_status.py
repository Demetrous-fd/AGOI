# Generated by Django 4.0.10 on 2023-06-02 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_report_user_reportscanneditem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportscanneditem',
            name='status',
            field=models.CharField(choices=[('ok', 'OK'), ('error', 'Не был в списке инвентаризации')], default='ok', max_length=8),
        ),
    ]
