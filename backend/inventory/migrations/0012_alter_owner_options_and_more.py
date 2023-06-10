# Generated by Django 4.2.2 on 2023-06-07 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_reportscanneditem_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='owner',
            options={'verbose_name': 'МОЛ', 'verbose_name_plural': 'МОЛЫ'},
        ),
        migrations.AlterField(
            model_name='historicalinstance',
            name='inventory_number',
            field=models.CharField(db_index=True, max_length=32, verbose_name='Инвентарный номер'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='inventory_number',
            field=models.CharField(db_index=True, max_length=32, unique=True, verbose_name='Инвентарный номер'),
        ),
    ]