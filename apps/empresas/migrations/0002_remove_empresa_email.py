# Generated by Django 5.0.6 on 2024-07-06 05:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empresa',
            name='email',
        ),
    ]
