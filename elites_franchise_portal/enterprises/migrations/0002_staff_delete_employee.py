# Generated by Django 4.1.1 on 2022-11-23 13:45

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('enterprises', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
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
                ('staff_number', models.CharField(max_length=300)),
                ('staff_type', models.CharField(choices=[('CASUAL', 'CASUAL'), ('CONTRACT', 'CONTRACT'), ('EMPLOYEE', 'EMPLOYEE')], default='EMPLOYEE', max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
    ]
