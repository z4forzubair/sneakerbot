# Generated by Django 3.2.1 on 2021-07-02 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('churchaio', '0017_auto_20210702_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='renew_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
