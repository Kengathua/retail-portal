# Generated by Django 4.0.4 on 2022-08-10 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('created_by', models.UUIDField(editable=False)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_by', models.UUIDField()),
                ('franchise', models.CharField(max_length=250)),
                ('customer_number', models.CharField(db_index=True, max_length=256)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('other_names', models.CharField(blank=True, max_length=256, null=True)),
                ('last_name', models.CharField(max_length=256)),
                ('account_number', models.CharField(blank=True, max_length=300, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')], max_length=24, null=True)),
                ('join_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_vip', models.BooleanField(default=False)),
                ('is_franchise', models.BooleanField(default=False)),
                ('id_no', models.CharField(blank=True, max_length=256, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=256, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('pushed_to_edi', models.BooleanField(default=False)),
                ('franchise_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
