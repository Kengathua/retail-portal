# Generated by Django 4.1.1 on 2022-11-08 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debit', '0007_purchasesreturn_return_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasesreturn',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]