# Generated by Django 4.0.4 on 2022-09-03 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_referencecatalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencecatalog',
            name='quantity_on_deposit',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
