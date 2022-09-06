# Generated by Django 4.0.4 on 2022-09-09 23:27

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('guid', models.UUIDField(unique=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('other_names', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('password', models.CharField(max_length=255)),
                ('date_of_birth', models.DateField(blank=True, default='1900-01-01', null=True)),
                ('updated_on', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('enterprise', models.CharField(max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ('first_name', 'last_name'),
            },
        ),
    ]
