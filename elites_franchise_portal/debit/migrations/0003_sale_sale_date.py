# Generated by Django 4.1.1 on 2022-11-03 10:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('debit', '0002_purchasesreturn'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='sale_date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
