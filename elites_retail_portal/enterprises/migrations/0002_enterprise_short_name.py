# Generated by Django 4.1.1 on 2023-01-31 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprises', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprise',
            name='short_name',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
