# Generated by Django 4.1.1 on 2022-11-18 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise_mgt', '0002_enterprisesetuprule_is_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprisesetuprulecatalog',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='enterprisesetupruleinventory',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='enterprisesetuprulewarehouse',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]