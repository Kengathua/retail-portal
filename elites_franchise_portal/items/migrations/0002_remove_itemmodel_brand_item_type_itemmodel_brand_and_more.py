# Generated by Django 4.0.4 on 2022-08-23 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemmodel',
            name='brand_item_type',
        ),
        migrations.AddField(
            model_name='itemmodel',
            name='brand',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='items.brand'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itemmodel',
            name='item_type',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='items.itemtype'),
            preserve_default=False,
        ),
    ]
