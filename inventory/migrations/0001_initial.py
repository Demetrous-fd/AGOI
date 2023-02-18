# Generated by Django 3.2.16 on 2023-02-18 07:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Адрес',
                'verbose_name_plural': 'Адреса',
            },
        ),
        migrations.CreateModel(
            name='ContractNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=128, unique=True, verbose_name='Номер контракта')),
            ],
            options={
                'verbose_name': 'Номер контракта',
                'verbose_name_plural': 'Номера контрактов',
            },
        ),
        migrations.CreateModel(
            name='EquipmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Тип оборудования')),
            ],
            options={
                'verbose_name': 'Тип оборудования',
                'verbose_name_plural': 'Типы оборудования',
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=32, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=32, verbose_name='Фамилия')),
                ('last_name', models.CharField(max_length=32, verbose_name='Отчество')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
            },
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('short_name', models.CharField(max_length=32, verbose_name='Короткое название')),
                ('slug', models.SlugField(max_length=128, unique=True, verbose_name='URL')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='Изображение')),
                ('equipment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.equipmenttype', verbose_name='Тип оборудования')),
            ],
            options={
                'verbose_name': 'Объект',
                'verbose_name_plural': 'Объекты',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Помещение')),
                ('address', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='inventory.address', verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Место нахождения',
                'verbose_name_plural': 'Локации',
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('inventory_number', models.CharField(default='Не указан', max_length=32, verbose_name='Инвентарный номер')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('contract_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.contractnumber', verbose_name='Номер контракта')),
                ('location', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.location', verbose_name='Место нахождения')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.object', verbose_name='Объект')),
                ('owner', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.owner', verbose_name='Владелец')),
                ('state', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.state', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Оборудование',
                'verbose_name_plural': 'Оборудование',
            },
        ),
        migrations.CreateModel(
            name='HistoricalInstance',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('inventory_number', models.CharField(default='Не указан', max_length=32, verbose_name='Инвентарный номер')),
                ('created_at', models.DateTimeField(blank=True, editable=False, verbose_name='Дата добавления')),
                ('history_change_reason', models.TextField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('contract_number', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.contractnumber', verbose_name='Номер контракта')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.location', verbose_name='Место нахождения')),
                ('object', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.object', verbose_name='Объект')),
                ('owner', models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.owner', verbose_name='Владелец')),
                ('state', models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.state', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'historical Оборудование',
                'verbose_name_plural': 'historical Оборудование',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalConsumable',
            fields=[
                ('written_off', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Количество списаных расходников')),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('balance', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Остаток')),
                ('initial_quantity', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Изначальное количество')),
                ('history_change_reason', models.TextField(null=True, verbose_name='Комментарий')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='inventory.location', verbose_name='Место нахождения')),
            ],
            options={
                'verbose_name': 'historical Расходник',
                'verbose_name_plural': 'historical Расходники',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Consumable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('balance', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Остаток')),
                ('initial_quantity', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Изначальное количество')),
                ('contract_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.contractnumber', verbose_name='Номер контракта')),
                ('location', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.location', verbose_name='Место нахождения')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.object', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Расходник',
                'verbose_name_plural': 'Расходники',
            },
        ),
    ]
