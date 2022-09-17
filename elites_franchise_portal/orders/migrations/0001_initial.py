# Generated by Django 4.1.1 on 2022-10-04 19:54

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import elites_franchise_portal.orders.models.orders
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('encounters', '0001_initial'),
        ('customers', '0001_initial'),
        ('catalog', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('cart_code', models.CharField(blank=True, max_length=250, null=True)),
                ('order_guid', models.UUIDField(blank=True, null=True)),
                ('is_empty', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_checked_out', models.BooleanField(default=False)),
                ('is_enterprise', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
                ('encounter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='encounters.encounter')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('opening_quantity', models.FloatField(blank=True, default=0, null=True)),
                ('quantity_added', models.FloatField(default=0)),
                ('closing_quantity', models.FloatField(blank=True, default=0, null=True)),
                ('selling_price', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('is_installment', models.BooleanField(default=False)),
                ('order_now', models.BooleanField(default=False)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.cart')),
                ('catalog_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.catalogitem')),
            ],
            options={
                'ordering': ['-closing_quantity', 'catalog_item__inventory_item__item__item_name'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('cart_code', models.CharField(blank=True, max_length=300, null=True)),
                ('order_number', models.CharField(blank=True, max_length=250, null=True)),
                ('order_name', models.CharField(blank=True, max_length=300, null=True)),
                ('order_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('instant_order_total', models.FloatField(blank=True, null=True)),
                ('installment_order_total', models.FloatField(blank=True, null=True)),
                ('order_total', models.FloatField(blank=True, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_cleared', models.BooleanField(default=False)),
                ('is_enterprise', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
            ],
            options={
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='OrderTransaction',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('order_transaction_code', models.CharField(default=elites_franchise_portal.orders.models.orders.create_order_transaction_code, max_length=300)),
                ('order_transaction_name', models.CharField(default=elites_franchise_portal.orders.models.orders.create_order_transaction_name, max_length=300)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.order')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.transaction')),
            ],
            options={
                'ordering': ['-order'],
            },
        ),
        migrations.CreateModel(
            name='OrderStatusLog',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('status_from', models.CharField(choices=[('PENDING', 'PENDING'), ('CONFIRMED', 'CONFIRMED'), ('CANCELED', 'CANCELED')], max_length=250)),
                ('status_to', models.CharField(choices=[('PENDING', 'PENDING'), ('CONFIRMED', 'CONFIRMED'), ('CANCELED', 'CANCELED')], max_length=250)),
                ('transition_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.order')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstantOrderItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('quantity', models.FloatField(default=0)),
                ('confirmation_status', models.CharField(choices=[('PENDING', 'PENDING'), ('CONFIRMED', 'CONFIRMED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=250)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('amount_due', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('payment_is_processed', models.BooleanField(default=False)),
                ('payment_status', models.CharField(choices=[('NOT PAID', 'NOT PAID'), ('DEPOSIT PAID', 'DEPOSIT PAID'), ('DEPOSIT PARTIALLY PAID', 'DEPOSIT PARTIALLY PAID'), ('PARTIALLY PAID', 'PARTIALLY PAID'), ('FULLY PAID', 'FULLY PAID'), ('NOT PAID AND RETURNED', 'NOT PAID AND RETURNED'), ('PARTIALLY PAID AND RETURNED', 'PARTIALLY PAID AND RETURNED')], default='NOT PAID', max_length=250)),
                ('quantity_cleared', models.IntegerField(default=0)),
                ('quantity_awaiting_clearance', models.IntegerField(default=0)),
                ('quantity_returned', models.IntegerField(default=0)),
                ('is_cleared', models.BooleanField(default=False)),
                ('cart_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.cartitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.order')),
            ],
            options={
                'ordering': ['-cart_item__catalog_item__inventory_item__item__item_name', '-total_amount'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstallmentsOrderItem',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('quantity', models.FloatField(default=0)),
                ('confirmation_status', models.CharField(choices=[('PENDING', 'PENDING'), ('CONFIRMED', 'CONFIRMED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=250)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('amount_due', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('payment_is_processed', models.BooleanField(default=False)),
                ('payment_status', models.CharField(choices=[('NOT PAID', 'NOT PAID'), ('DEPOSIT PAID', 'DEPOSIT PAID'), ('DEPOSIT PARTIALLY PAID', 'DEPOSIT PARTIALLY PAID'), ('PARTIALLY PAID', 'PARTIALLY PAID'), ('FULLY PAID', 'FULLY PAID'), ('NOT PAID AND RETURNED', 'NOT PAID AND RETURNED'), ('PARTIALLY PAID AND RETURNED', 'PARTIALLY PAID AND RETURNED')], default='NOT PAID', max_length=250)),
                ('quantity_cleared', models.IntegerField(default=0)),
                ('quantity_awaiting_clearance', models.IntegerField(default=0)),
                ('quantity_returned', models.IntegerField(default=0)),
                ('is_cleared', models.BooleanField(default=False)),
                ('deposit_amount', models.FloatField(blank=True, default=0, null=True)),
                ('payment_plan', models.CharField(choices=[('DAILY', 'DAILY'), ('2 DAYS', '2 DAYS'), ('WEEKLY', 'WEEKLY'), ('2 WEEKS', '2 WEEKS'), ('MONTHLY', 'MONTHLY')], default='MONTHLY', max_length=250)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('speculated_end_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('preference_level', models.CharField(choices=[('LOW', 'LOW'), ('EQUAL', 'EQUAL'), ('NORMAL', 'NORMAL'), ('MODERATE', 'MODERATE'), ('HIGH', 'HIGH'), ('VERY HIGH', 'VERY HIGH')], default='NORMAL', max_length=300)),
                ('preference_type', models.CharField(choices=[('FLAT', 'FLAT'), ('PERCENTAGE', 'PERCENTAGE'), ('RATIO', 'RATIO')], default='RATIO', max_length=300)),
                ('share_value', models.FloatField(blank=True, default=1, null=True)),
                ('quantity_on_full_deposit', models.IntegerField(default=0)),
                ('quantity_on_partial_deposit', models.IntegerField(default=0)),
                ('quantity_without_deposit', models.IntegerField(blank=True, null=True)),
                ('cart_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.cartitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='orders.order')),
            ],
            options={
                'ordering': ['-cart_item__catalog_item__inventory_item__item__item_name', '-total_amount'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Installment',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('installment_code', models.CharField(blank=True, max_length=300, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('installment_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('next_installment_date', models.DateField(blank=True, null=True)),
                ('installment_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.installmentsorderitem')),
            ],
            options={
                'ordering': ['-installment_date'],
            },
        ),
    ]
