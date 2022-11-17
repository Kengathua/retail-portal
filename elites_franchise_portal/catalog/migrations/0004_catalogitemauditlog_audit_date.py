# Generated by Django 4.1.1 on 2022-11-16 16:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_catalogitemauditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitemauditlog',
            name='audit_date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
