# Generated by Django 4.1.1 on 2023-02-20 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_cartitem_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
        migrations.AddField(
            model_name='installmentsorderitem',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
        migrations.AddField(
            model_name='instantorderitem',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED')], default='PENDING', max_length=300),
        ),
        migrations.AddField(
            model_name='ordertransaction',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED'), ('RECEIVED', 'RECEIVED')], default='PENDING', max_length=300),
        ),
    ]
