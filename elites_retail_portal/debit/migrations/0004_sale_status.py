# Generated by Django 4.1.1 on 2023-02-20 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debit', '0003_saleitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
    ]
