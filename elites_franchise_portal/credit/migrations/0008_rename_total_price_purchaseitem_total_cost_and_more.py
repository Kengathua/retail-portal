# Generated by Django 4.1.1 on 2022-11-07 20:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0007_rename_item_salesreturn_sale_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseitem',
            old_name='total_price',
            new_name='total_cost',
        ),
        migrations.RenameField(
            model_name='purchaseitem',
            old_name='unit_price',
            new_name='unit_cost',
        ),
        migrations.AddField(
            model_name='salesreturn',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=30, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]