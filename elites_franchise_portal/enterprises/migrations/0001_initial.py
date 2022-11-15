# Generated by Django 4.1.1 on 2022-11-15 10:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import elites_franchise_portal.common.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('other_names', models.CharField(blank=True, max_length=256, null=True)),
                ('last_name', models.CharField(max_length=256)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')], max_length=24, null=True)),
                ('join_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('id_no', models.CharField(blank=True, max_length=256, null=True)),
                ('id_type', models.CharField(blank=True, choices=[('NATIONAL ID', 'NATIONAL ID'), ('MILITARY ID', 'MILITARY ID'), ('PASSPORT', 'PASSPORT')], max_length=300, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=256, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('agent_number', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('enterprise', models.CharField(max_length=250)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('other_names', models.CharField(blank=True, max_length=256, null=True)),
                ('last_name', models.CharField(max_length=256)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')], max_length=24, null=True)),
                ('join_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('id_no', models.CharField(blank=True, max_length=256, null=True)),
                ('id_type', models.CharField(blank=True, choices=[('NATIONAL ID', 'NATIONAL ID'), ('MILITARY ID', 'MILITARY ID'), ('PASSPORT', 'PASSPORT')], max_length=300, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=256, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('employee_number', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('reg_no', models.CharField(blank=True, max_length=300, null=True)),
                ('name', models.CharField(max_length=300)),
                ('enterprise_code', models.CharField(blank=True, max_length=300, null=True, unique=True, validators=[elites_franchise_portal.common.validators.franchise_enterprise_code_validator])),
                ('enterprise_type', models.CharField(choices=[('FRANCHISE', 'FRANCHISE'), ('SUPPLIER', 'SUPPLIER'), ('INDEPENDENT', 'INDEPENDENT')], default='FRANCHISE', max_length=300)),
                ('main_branch_code', models.CharField(blank=True, db_index=True, max_length=300, null=True)),
                ('is_main_branch', models.BooleanField(default=True)),
                ('business_type', models.CharField(blank=True, choices=[('AGENT', 'AGENT'), ('SHOP', 'SHOP'), ('SUPERMARKET', 'SUPERMARKET'), ('WHOLESALE', 'WHOLESALE')], default='SHOP', max_length=300, null=True)),
                ('supplier_type', models.CharField(blank=True, choices=[('IMPORTER', 'IMPORTER'), ('SERVICES', 'SERVICES'), ('WHOLESALER', 'WHOLESALER'), ('DISTRIBUTOR', 'DISTRIBUTOR'), ('MANUFACTURER', 'MANUFACTURER'), ('DROP SHIPPER', 'DROP SHIPPER'), ('SUB CONTRACTOR', 'SUB CONTRACTOR'), ('TRADE SHOW REP', 'TRADE SHOW REP'), ('INDEPENDENT SUPPLIER', 'INDEPENDENT SUPPLIER')], max_length=300, null=True)),
                ('dissolution_date', models.DateField(blank=True, db_index=True, null=True)),
                ('dissolution_reason', models.TextField(blank=True, null=True)),
                ('is_cleaned', models.BooleanField(default=False)),
                ('pushed_to_edi', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('social_platform', models.CharField(choices=[('FACEBOOK', 'FACEBOOK'), ('TWITTER', 'TWITTER'), ('INSTAGRAM', 'INSTAGRAM'), ('WHATSAPP', 'WHATSAPP')], max_length=250)),
                ('link', models.URLField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=300, null=True)),
                ('account_no', models.CharField(blank=True, max_length=300, null=True)),
                ('enterprise', models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, related_name='platform_Enterprise', to='enterprises.enterprise')),
            ],
            options={
                'ordering': ('-updated_on', '-created_on'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnterpriseContact',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phoneNumber', models.CharField(max_length=16, unique=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{8,15}$')])),
                ('address', models.TextField(blank=True, null=True)),
                ('enterprise', models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, related_name='contact_enterprise', to='enterprises.enterprise')),
            ],
            options={
                'ordering': ('-updated_on', '-created_on'),
                'abstract': False,
            },
        ),
    ]
