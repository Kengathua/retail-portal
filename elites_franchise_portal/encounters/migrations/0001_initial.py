# Generated by Django 4.0.4 on 2022-09-09 23:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('billing', models.JSONField()),
                ('payments', models.JSONField(blank=True, null=True)),
                ('submitted_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('payable_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('balance_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('processing_status', models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300)),
                ('stalling_reason', models.TextField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
