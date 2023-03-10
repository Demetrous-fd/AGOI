# Generated by Django 4.0.10 on 2023-03-06 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_remove_object_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractnumber',
            name='number',
            field=models.CharField(db_index=True, max_length=128, unique=True, verbose_name='Номер контракта'),
        ),
        migrations.AlterField(
            model_name='historicalinstance',
            name='inventory_number',
            field=models.CharField(db_index=True, default='Не указан', max_length=32, verbose_name='Инвентарный номер'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='inventory_number',
            field=models.CharField(db_index=True, default='Не указан', max_length=32, verbose_name='Инвентарный номер'),
        ),
        migrations.AlterField(
            model_name='object',
            name='name',
            field=models.CharField(db_index=True, max_length=256, verbose_name='Название'),
        ),
    ]
