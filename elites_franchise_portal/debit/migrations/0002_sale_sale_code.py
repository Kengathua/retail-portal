# Generated by Django 4.0.4 on 2022-08-11 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='sale_code',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
