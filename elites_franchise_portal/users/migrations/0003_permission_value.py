# Generated by Django 4.1.1 on 2022-11-13 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_group_permission_role_userrole_grouppermission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='value',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
    ]
