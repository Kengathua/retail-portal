# Generated by Django 4.1.1 on 2023-01-03 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='units',
            name='units_quantity',
            field=models.FloatField(default=1),
        ),
        migrations.AddField(
            model_name='units',
            name='units_type',
            field=models.CharField(choices=[('LITRES', 'LITRES'), ('MILILITRES', 'MILILITRES'), ('KILOGRAMS', 'KILOGRAMS'), ('POUNDS', 'POUNDS'), ('OUNCES', 'OUNCES'), ('GRAMS', 'GRAMS'), ('CARTONS', 'CARTONS'), ('PACKETS', 'PACKETS'), ('SACHETS', 'SACHETS'), ('PIECES', 'PIECES'), ('SACKS', 'SACKS'), ('BALES', 'BALES'), ('INCHES', 'INCHES'), ('METRES', 'METRES'), ('CENTIMETRES', 'CENTIMETRES'), ('DOZENS', 'DOZENS')], default='PIECES', max_length=300),
        ),
    ]
