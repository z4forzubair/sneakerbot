# Generated by Django 3.2.1 on 2021-05-18 17:31

import creditcards.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('churchaio', '0010_auto_20210518_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='cc_code',
            field=creditcards.models.SecurityCodeField(max_length=4, verbose_name='security code'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='cc_expiry',
            field=creditcards.models.CardExpiryField(verbose_name='expiration date'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='cc_number',
            field=creditcards.models.CardNumberField(max_length=25, verbose_name='card number'),
        ),
    ]
