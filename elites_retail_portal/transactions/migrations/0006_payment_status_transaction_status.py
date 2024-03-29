# Generated by Django 4.1.1 on 2023-02-20 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_payment_payment_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED'), ('RECEIVED', 'RECEIVED')], default='RECEIVED', max_length=300),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('FAILED', 'FAILED'), ('PENDING', 'PENDING'), ('ONGOING', 'ONGOING'), ('SUCCESS', 'SUCCESS'), ('STALLED', 'STALLED'), ('CANCELED', 'CANCELED'), ('RECEIVED', 'RECEIVED')], default='RECEIVED', max_length=300),
        ),
    ]
