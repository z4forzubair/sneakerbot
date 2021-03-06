# Generated by Django 3.2.1 on 2021-06-27 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('churchaio', '0015_auto_20210624_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(choices=[('VIC', 'VIC'), ('WA', 'WA'), ('TAS', 'TAS'), ('QLD', 'QLD'), ('NT', 'NT'), ('SA', 'SA'), ('NSW', 'NSW'), ('ACT', 'ACT')], default='VIC', max_length=4),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeout', models.PositiveSmallIntegerField()),
                ('retry', models.PositiveIntegerField()),
                ('monitor', models.PositiveIntegerField()),
                ('sleep', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
