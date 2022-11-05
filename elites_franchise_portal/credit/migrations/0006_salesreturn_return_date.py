# Generated by Django 4.1.1 on 2022-11-05 09:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0005_alter_salesreturn_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesreturn',
            name='return_date',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]