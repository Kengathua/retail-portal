# Generated by Django 4.0.4 on 2022-08-27 10:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('franchise', models.CharField(max_length=250)),
                ('quantity_purchased', models.FloatField()),
                ('sale_units_purchased', models.FloatField(blank=True, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('unit_marked_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('purchase_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('quantity_to_inventory', models.FloatField(blank=True, null=True)),
                ('quantity_to_inventory_on_display', models.FloatField(blank=True, null=True)),
                ('quantity_to_inventory_in_warehouse', models.FloatField(blank=True, null=True)),
                ('move_in_bulk', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='items.item')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
