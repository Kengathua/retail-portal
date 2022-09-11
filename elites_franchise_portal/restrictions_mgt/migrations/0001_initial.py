# Generated by Django 4.0.4 on 2022-09-10 10:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('warehouses', '0001_initial'),
        ('debit', '0001_initial'),
        ('catalog', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnterpriseSetup',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseSetupRules',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('default_catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='default_catalog', to='catalog.catalog')),
                ('default_inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='default_inventory', to='debit.inventory')),
                ('default_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='default_warehouse', to='warehouses.warehouse')),
                ('landing_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='landing_warehouse', to='warehouses.warehouse')),
                ('master_inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='master_inventory', to='debit.inventory')),
                ('standard_catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='standard_catalog', to='catalog.catalog')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]