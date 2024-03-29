# Generated by Django 4.1.1 on 2023-02-08 09:15

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('inventory_name', models.CharField(max_length=300)),
                ('inventory_code', models.CharField(blank=True, max_length=300, null=True)),
                ('inventory_type', models.CharField(choices=[('EXCESS', 'EXCESS'), ('SERVICE', 'SERVICE'), ('AVAILABLE', 'AVAILABLE'), ('ALLOCATED', 'ALLOCATED'), ('DECOUPLING', 'DECOUPLING'), ('THEORETICAL', 'THEORETICAL'), ('SAFETY STOCK', 'SAFETY STOCK'), ('WORKING STOCK', 'WORKING STOCK'), ('PSYCHIC STOCK', 'PSYCHIC STOCK'), ('RAW MATERIALS', 'RAW MATERIALS'), ('FINISHED GOODS', 'FINISHED GOODS'), ('WORK IN PROCESS', 'WORK IN PROCESS'), ('IN TRANSIT STOCK', 'IN TRANSIT STOCK'), ('PACKING MATERIALS', 'PACKING MATERIALS'), ('ANTICIPATORY STOCK', 'ANTICIPATORY STOCK'), ('MAINTENANCE, REPAIR AND OPERATING', 'MAINTENANCE, REPAIR AND OPERATING')], default='WORKING STOCK', max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_master', models.BooleanField(default=False)),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('pushed_to_edi', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryInventoryItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('pushed_to_edi', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['item__item_name'],
            },
        ),
        migrations.CreateModel(
            name='InventoryRecord',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('record_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('record_code', models.CharField(blank=True, max_length=300, null=True)),
                ('opening_stock_quantity', models.FloatField(blank=True, default=0, null=True)),
                ('opening_stock_total_amount', models.FloatField(blank=True, default=0, null=True)),
                ('record_type', models.CharField(choices=[('ADD', 'ADD'), ('REMOVE', 'REMOVE')], default='ADD', max_length=300)),
                ('quantity_recorded', models.FloatField()),
                ('unit_price', models.FloatField()),
                ('total_amount_recorded', models.FloatField(blank=True, null=True)),
                ('removal_type', models.CharField(blank=True, choices=[('SALES', 'SALES'), ('DAMAGES', 'DAMAGES'), ('SAFETY STOCK', 'SAFETY STOCK'), ('SALES RETURNS', 'SALES RETURNS'), ('PURCHASES RETURNS', 'PURCHASES RETURNS')], max_length=300, null=True)),
                ('removal_guid', models.UUIDField(blank=True, null=True)),
                ('addition_guid', models.UUIDField(blank=True, null=True)),
                ('closing_stock_quantity', models.FloatField(blank=True, default=0, null=True)),
                ('closing_stock_total_amount', models.FloatField(blank=True, default=0, null=True)),
                ('quantity_of_stock_on_display', models.FloatField(blank=True, null=True)),
                ('quantity_of_stock_in_warehouse', models.FloatField(blank=True, null=True)),
                ('quantity_of_stock_on_sale', models.FloatField(blank=True, null=True)),
                ('quantity_sold', models.FloatField(blank=True, null=True)),
                ('remaining_stock_total_amount', models.FloatField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_catalog', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['inventory_item__item__item_name'],
            },
        ),
        migrations.CreateModel(
            name='PurchasesReturn',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('quantity_returned', models.FloatField()),
                ('unit_cost', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('total_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('notes', models.TextField(blank=True, null=True)),
                ('return_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('sale_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('sale_code', models.CharField(blank=True, max_length=300, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('data', models.JSONField(blank=True, null=True)),
                ('receipt_number', models.CharField(blank=True, max_length=300, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_cleared', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('sale_type', models.CharField(choices=[('INSTANT', 'INSTANT'), ('INSTALLMENT', 'INSTALLMENT')], default='INSTANT', max_length=300)),
                ('selling_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('quantity_sold', models.FloatField()),
                ('processing_status', models.CharField(choices=[('PENDING', 'PENDING'), ('CANCELED', 'CANCELED'), ('REJECTED', 'REJECTED'), ('CONFIRMED', 'CONFIRMED'), ('PROCESSED', 'PROCESSED')], default='PENDING', max_length=300)),
                ('is_cleared', models.BooleanField(default=False)),
                ('catalog_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.catalogitem')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='debit.sale', verbose_name='sales')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
