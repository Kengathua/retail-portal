# Generated by Django 4.1.1 on 2022-11-24 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enterprises', '0001_initial'),
        ('credit', '0001_initial'),
        ('debit', '0001_initial'),
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesreturn',
            name='sale',
            field=models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, to='debit.sale'),
        ),
        migrations.AddField(
            model_name='salesreturn',
            name='sale_item',
            field=models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, to='debit.saleitem'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='items.item'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='purchase',
            field=models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_purchase', to='credit.purchase'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='supplier',
            field=models.ForeignKey(max_length=250, on_delete=django.db.models.deletion.PROTECT, related_name='supplier_enterprise', to='enterprises.enterprise'),
        ),
    ]
