# Generated by Django 4.0.4 on 2022-08-27 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('debit', '0001_initial'),
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogitem',
            name='inventory_item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='debit.inventoryitem'),
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.section'),
        ),
        migrations.AddField(
            model_name='catalogcatalogitem',
            name='catalog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_catalogcatalogitem', to='catalog.catalog'),
        ),
        migrations.AddField(
            model_name='catalogcatalogitem',
            name='catalog_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_item_catalogcatalogitem', to='catalog.catalogitem'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='catalog_items',
            field=models.ManyToManyField(related_name='catalogitem', through='catalog.CatalogCatalogItem', to='catalog.catalogitem'),
        ),
    ]
