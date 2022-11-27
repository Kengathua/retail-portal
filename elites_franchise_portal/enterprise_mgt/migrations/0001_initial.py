# Generated by Django 4.1.1 on 2022-11-27 16:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('debit', '0001_initial'),
        ('catalog', '0001_initial'),
        ('enterprises', '0001_initial'),
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnterpriseSetupRule',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('is_default', models.BooleanField(default=True)),
                ('supports_installment_sales', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseSetupRuleWarehouse',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprise_mgt.enterprisesetuprule')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouses.warehouse')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseSetupRuleInventory',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='debit.inventory')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprise_mgt.enterprisesetuprule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseSetupRuleCatalog',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.catalog')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enterprise_mgt.enterprisesetuprule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='enterprisesetuprule',
            name='catalogs',
            field=models.ManyToManyField(related_name='rulecatalog', through='enterprise_mgt.EnterpriseSetupRuleCatalog', to='catalog.catalog'),
        ),
        migrations.AddField(
            model_name='enterprisesetuprule',
            name='inventories',
            field=models.ManyToManyField(related_name='ruleinventory', through='enterprise_mgt.EnterpriseSetupRuleInventory', to='debit.inventory'),
        ),
        migrations.AddField(
            model_name='enterprisesetuprule',
            name='warehouses',
            field=models.ManyToManyField(related_name='rulewarehouse', through='enterprise_mgt.EnterpriseSetupRuleWarehouse', to='warehouses.warehouse'),
        ),
        migrations.CreateModel(
            name='EnterpriseSetup',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('setup_name', models.CharField(max_length=300)),
                ('is_active', models.BooleanField(default=False)),
                ('enterprise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='enterprises.enterprise')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
