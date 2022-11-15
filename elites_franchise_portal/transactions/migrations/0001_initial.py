# Generated by Django 4.1.1 on 2022-11-15 10:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('encounters', '0001_initial'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentRequest',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('payment_id', models.UUIDField(blank=True, null=True)),
                ('business_account_number', models.CharField(blank=True, max_length=300, null=True)),
                ('client_account_number', models.CharField(blank=True, max_length=300, null=True)),
                ('request_from_account_number', models.CharField(blank=True, max_length=300, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=300, null=True)),
                ('business_short_code', models.CharField(blank=True, max_length=200, null=True)),
                ('business_passkey', models.CharField(blank=True, max_length=200, null=True)),
                ('requested_amount', models.DecimalField(decimal_places=2, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('paid_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('service', models.CharField(max_length=300)),
                ('service_type', models.CharField(max_length=300)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS'), ('FAILED', 'FAILED')], default='PENDING', max_length=300)),
                ('message', models.CharField(blank=True, max_length=300, null=True)),
                ('receipt_no', models.CharField(blank=True, max_length=300, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('auto_process_payment', models.BooleanField(default=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('checkout_request_id', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('transaction_code', models.CharField(blank=True, max_length=250, null=True)),
                ('payment_code', models.CharField(blank=True, max_length=300, null=True)),
                ('wallet_code', models.CharField(blank=True, max_length=250, null=True)),
                ('account_number', models.CharField(blank=True, max_length=250, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('reservation_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('reservation_type', models.CharField(blank=True, choices=[('FLAT', 'FLAT'), ('PERCENTAGE', 'PERCENTAGE'), ('NO RESERVATION', 'NO RESERVATION')], default='NO RESERVATION', max_length=300, null=True)),
                ('reserve_at', models.CharField(blank=True, choices=[('WALLET', 'WALLET'), ('OTHER', 'OTHER')], default='WALLET', max_length=300, null=True)),
                ('transaction_time', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('transaction_type', models.CharField(choices=[('DEPOSIT', 'DEPOSIT'), ('WITHDRAW', 'WITHDRAW'), ('TRANSFER', 'TRANSFER')], default='DEPOSIT', max_length=250)),
                ('transaction_means', models.CharField(choices=[('CASH', 'CASH'), ('CARD', 'CARD'), ('WALLET', 'WALLET'), ('MPESA TILL', 'MPESA TILL'), ('MPESA PAYBILL', 'MPESA PAYBILL'), ('BANK WIRE TRANSFER', 'BANK WIRE TRANSFER')], default='CASH', max_length=250)),
                ('transaction_processed', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('payment_code', models.CharField(blank=True, max_length=300, null=True)),
                ('account_number', models.CharField(blank=True, max_length=300, null=True)),
                ('required_amount', models.DecimalField(decimal_places=2, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('paid_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('balance_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('payment_method', models.CharField(default='CASH', max_length=300)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
                ('encounter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='encounters.encounter')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
