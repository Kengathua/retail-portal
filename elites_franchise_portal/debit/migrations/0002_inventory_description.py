# Generated by Django 4.0.4 on 2022-09-11 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
