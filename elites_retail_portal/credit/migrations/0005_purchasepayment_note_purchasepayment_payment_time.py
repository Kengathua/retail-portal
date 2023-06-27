# Generated by Django 4.1.1 on 2023-02-13 12:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0004_purchasepayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasepayment',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='purchasepayment',
            name='payment_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
