# Generated by Django 4.1.1 on 2022-10-25 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='barcode',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]