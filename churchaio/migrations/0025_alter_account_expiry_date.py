# Generated by Django 3.2.1 on 2021-08-25 09:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchaio', '0024_configuration_auto_solve'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiry_date',
            field=models.DateField(default=datetime.date(2021, 8, 25)),
            preserve_default=False,
        ),
    ]